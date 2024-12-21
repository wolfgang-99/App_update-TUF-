# local import
from __future__ import annotations
import os
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

from securesystemslib.signer import CryptoSigner, Signer
from cryptography.hazmat.primitives.asymmetric import ec

# tuf import
from tuf.api.metadata import (
    SPECIFICATION_VERSION,
    Metadata,
    Root,
    Snapshot,
    TargetFile,
    Targets,
    Timestamp,
)
from tuf.api.serialization.json import JSONSerializer

# personal import
from export_key import export_key


def _in(days: float) -> datetime:
    """Adds 'days' to now and returns datetime object w/o microseconds."""
    return datetime.now(timezone.utc).replace(microsecond=0) + timedelta(days=days)


# Create top-level metadata
# =========================
# Every TUF repository has at least four roles, i.e. the top-level roles
# 'targets', 'snapshot', 'timestamp' and 'root'. Below we will discuss their
# purpose, show how to create the corresponding metadata, and how to use them
# to provide integrity, consistency and freshness for the files TUF aims to
# protect, i.e. target files.

# Common fields
# -------------
# All roles have the same metadata container format, for which the metadata API
# provides a generic 'Metadata' class. This class has two fields, one for
# cryptographic signatures, i.e. 'signatures', and one for the payload over
# which signatures are generated, i.e. 'signed'. The payload must be an
# instance of either 'Targets', 'Snapshot', 'Timestamp' or 'Root' class. Common
# fields in all of these 'Signed' classes are:
#
# spec_version -- The supported TUF specification version number.
# version -- The metadata version number.
# expires -- The metadata expiry date.
#
# The 'version', which is incremented on each metadata change, is used to
# reference metadata from within other metadata, and thus allows for repository
# consistency in addition to protecting against rollback attacks.
#
# The date the metadata 'expires' protects against freeze attacks and allows
# for implicit key revocation. Choosing an appropriate expiration interval
# depends on the volatility of a role and how easy it is to re-sign them.
# Highly volatile roles (timestamp, snapshot, targets), usually have shorter
# expiration intervals, whereas roles that change less and might use offline
# keys (root, delegating targets) may have longer expiration intervals.

SPEC_VERSION = ".".join(SPECIFICATION_VERSION)

# Define containers for role objects and cryptographic keys created below. This
# allows us to sign and write metadata in a batch more easily.
roles: dict[str, Metadata] = {}
signers: dict[str, Signer] = {}


# Targets (integrity)
# -------------------
# The targets role guarantees integrity for the files that TUF aims to protect,
# i.e. target files. It does so by listing the relevant target files, along
# with their hash and length.
roles["targets"] = Metadata(Targets(expires=_in(7)))

# For the purpose of this example we use the top-level targets role to protect
# the integrity of this very example script. The metadata entry contains the
# hash and length of this file at the local path. In addition, it specifies the
# 'target path', which a client uses to locate the target file relative to a
# configured mirror base URL.
#
#      |----base artifact URL---||-------target path-------|
# e.g. tuf-examples.org/artifacts/manual_repo/basic_repo.py

local_path = Path("targets/color_changer.exe").resolve()
target_path = f"targets/{local_path.parts[-1]}"

target_file_info = TargetFile.from_file(target_path, str(local_path))
roles["targets"].signed.targets[target_path] = target_file_info

# Snapshot (consistency)
# ----------------------
# The snapshot role guarantees consistency of the entire repository. It does so
# by listing all available targets metadata files at their latest version. This
# becomes relevant, when there are multiple targets metadata files in a
# repository and we want to protect the client against mix-and-match attacks.
roles["snapshot"] = Metadata(Snapshot(expires=_in(7)))

# Timestamp (freshness)
# ---------------------
# The timestamp role guarantees freshness of the repository metadata. It does
# so by listing the latest snapshot (which in turn lists all the latest
# targets) metadata. A short expiration interval requires the repository to
# regularly issue new timestamp metadata and thus protects the client against
# freeze attacks.
#
# Note that snapshot and timestamp use the same generic wireline metadata
# format. But given that timestamp metadata always has only one entry in its
# 'meta' field, i.e. for the latest snapshot file, the timestamp object
# provides the shortcut 'snapshot_meta'.
roles["timestamp"] = Metadata(Timestamp(expires=_in(7)))

# Root (root of trust)
# --------------------
# The root role serves as root of trust for all top-level roles, including
# itself. It does so by mapping cryptographic keys to roles, i.e. the keys that
# are authorized to sign any top-level role metadata, and signing thresholds,
# i.e. how many authorized keys are required for a given role (see 'roles'
# field). This is called top-level delegation.
#
# In addition, root provides all public keys to verify these signatures (see
# 'keys' field), and a configuration parameter that describes whether a
# repository uses consistent snapshots (see section 'Persist metadata' below
# for more details).

# Create root metadata object
roles["root"] = Metadata(Root(expires=_in(365)))

# For this code, we generate one key pair for each top-level role
# using securesystemslib.
# See https://github.com/secure-systems-lab/securesystemslib for more details
# about key handling, and don't forget to password-encrypt your private keys!
for name in ["targets", "snapshot", "timestamp", "root"]:
    private_key = ec.generate_private_key(ec.SECP256R1())
    signers[name] = CryptoSigner(private_key=private_key)
    roles["root"].signed.add_key(signers[name].public_key, name)

    # export and encrypt private key
    export_key(private_key=private_key, name=name)

# NOTE: We only need the public part to populate root, so it is possible to use
# out-of-band mechanisms to generate key pairs and only expose the public part
# to whoever maintains the root role. As a matter of fact, the very purpose of
# signature thresholds is to avoid having private keys all in one place.


# Sign top-level metadata (in-band)
# =================================
# In this example we have access to all top-level signing keys, so we can use
# them to create and add a signature for each role metadata.
for name in ["targets", "snapshot", "timestamp", "root"]:
    roles[name].sign(signers[name])


# Persist metadata (consistent snapshot)
# ======================================
# It is time to publish the first set of metadata for a client to safely
# download the target file that we have registered for this example repository.
#
# Also note that the TUF specification does not mandate a wireline format. In
# this demo we use a non-compact JSON format and store all metadata in
# temporary directory at CWD for review.
PRETTY = JSONSerializer(compact=False)
TMP_DIR = tempfile.mkdtemp(dir=os.getcwd())

for name in ["root", "targets", "snapshot"]:
    filename = f"{roles[name].signed.version}.{roles[name].signed.type}.json"
    path = os.path.join(TMP_DIR, filename)
    roles[name].to_file(path, serializer=PRETTY)

roles["timestamp"].to_file(os.path.join(TMP_DIR, "timestamp.json"), serializer=PRETTY)


# Snapshot + Timestamp + Sign + Persist
# -------------------------------------
# Sign and write metadata for all changed roles, i.e. all but root
for role_name in ["targets", "snapshot", "timestamp"]:
    roles[role_name].sign(signers[role_name])

    # Prefix all but timestamp with version number (see consistent snapshot)
    filename = f"{role_name}.json"
    if role_name != "timestamp":
        filename = f"{roles[role_name].signed.version}.{filename}"

    roles[role_name].to_file(os.path.join(TMP_DIR, filename), serializer=PRETTY)

