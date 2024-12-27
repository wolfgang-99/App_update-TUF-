import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

from tuf.api.metadata import Metadata
from tuf.api.metadata import TargetFile
from tuf.api.serialization.json import JSONSerializer
from securesystemslib.signer import CryptoSigner

from import_key import import_key


# Helper function to calculate expiration date
def _in(days: float) -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0) + timedelta(days=days)


# Define repository roles and metadata files
ROLES = ["root", "targets", "snapshot", "timestamp"]
METADATA_DIR = "metadata_repo"  # Directory where the metadata resides
PRIVATE_KEYS_DIR = "keys"  # Directory containing private key PEM files
PRETTY = JSONSerializer(compact=False)
last_version = 1
ROOT_LAST_VERSION = 1

# Step 1: Load existing metadata
metadata = {}
for role in ROLES:
    if role == "root":
        metadata_file = Path(METADATA_DIR) / f"{ROOT_LAST_VERSION}.{role}.json"
        with metadata_file.open("r") as f:
            metadata[role] = Metadata.from_file(str(metadata_file))
    elif role != "timestamp":
        metadata_file = Path(METADATA_DIR) / f"{last_version}.{role}.json"
        with metadata_file.open("r") as f:
            metadata[role] = Metadata.from_file(str(metadata_file))
    else:
        metadata_file = Path(METADATA_DIR) / f"{role}.json"
        with metadata_file.open("r") as f:
            metadata[role] = Metadata.from_file(str(metadata_file))

# Step 2: Import private keys for signing
signers = {}
for role in ROLES:
    private_key_path = Path(PRIVATE_KEYS_DIR) / f"{role}_private_key.pem"
    private_key = import_key(file_path=private_key_path)

    signers[role] = CryptoSigner(private_key=private_key)

# Step 3: Update the metadata
# Update Targets
metadata["targets"].signed.version += 1
metadata["targets"].signed.expires = _in(7)  # Set expiration 7 days from now

# Add or update target files (optional)
# adding a new file
new_target_path = Path("targets/color_changer.exe").resolve()
# new_target_relative_path = f"{new_target_path.parts[-2]}/{new_target_path.parts[-1]}"  # Relative path to target
new_target_relative_path = f"targets/{new_target_path.parts[-1]}"
metadata["targets"].signed.targets[new_target_relative_path] = TargetFile.from_file(new_target_relative_path, str(new_target_path))

# Update Snapshot
metadata["snapshot"].signed.version += 1
metadata["snapshot"].signed.expires = _in(7)  # Set expiration 7 days from now
metadata["snapshot"].signed.meta["targets.json"].version = metadata["targets"].signed.version

# Update Timestamp
metadata["timestamp"].signed.version += 1
metadata["timestamp"].signed.expires = _in(7)  # Set expiration 1 day from now
metadata["timestamp"].signed.snapshot_meta.version = metadata["snapshot"].signed.version

# Step 4: Sign updated metadata
for role in ["targets", "snapshot", "timestamp"]:
    metadata[role].sign(signers[role])

# Step 5: Save updated metadata to disk
# Save updated metadata to disk with consistent snapshot naming
for role in ["targets", "snapshot"]:
    # Use the version number from the metadata
    version = metadata[role].signed.version
    file_name = f"{version}.{role}.json"
    output_path = Path(METADATA_DIR) / file_name
    metadata[role].to_file(str(output_path), serializer=PRETTY)

# Save timestamp.json (always without version prefix)
metadata["timestamp"].to_file(f"{Path(METADATA_DIR)}/timestamp.json", serializer=PRETTY)


print("Repository metadata updated successfully.")


def update_root(metadata, tmp_dir):
    new_root_signer = CryptoSigner.generate_ecdsa()

    metadata["root"].signed.revoke_key(signers["root"].public_key.keyid, "root")
    metadata["root"].signed.add_key(new_root_signer.public_key, "root")
    metadata["root"].signed.version += 1

    metadata["root"].signatures.clear()
    for signer in [signers["root"], new_root_signer]:
        metadata["root"].sign(signer, append=True)

    metadata["root"].to_file(
        os.path.join(tmp_dir, f"{metadata['root'].signed.version}.root.json"),
        serializer=PRETTY,
    )
# tmp_dir = Path(METADATA_DIR)
# update_root(metadata,tmp_dir )