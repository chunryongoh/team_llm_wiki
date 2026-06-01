# DACON Leaderboard and Local OOF Claim Boundary

This packet captures a reporting boundary for the DACON/ETRI sleep-health hackathon.

Current team convention:

- Local GroupKFold OOF metrics are local validation evidence.
- DACON public leaderboard results are submission feedback and should be logged with submission metadata.
- DACON private leaderboard results, when available, are final leaderboard evidence and should not be merged with local OOF rows.
- Public leaderboard feedback should be treated as directional and potentially noisy unless paired with submission metadata, target configuration, preprocessing, feature set, model family, and timestamp.
- A local OOF result should not be promoted to a DACON leaderboard claim unless the matching submission record exists.

Known boundary:

- This packet is not organizer-official split protocol evidence.
- If DACON or organizer-official split/private leaderboard interpretation rules are later confirmed, they supersede this team reporting convention.
