import yaml
import os
import sys
from datetime import datetime

queue_path = "DIR-DS-000-agent-config/NC-CFG-DS-004-task-queue.yaml"
lock_path = "DIR-DS-000-agent-config/queue.lock"

# Generate worker identity
timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]
port = int(datetime.now().timestamp())
my_claim = f"worker-{port}-723033"

print(f"MY_CLAIM: {my_claim}")
print(f"TIMESTAMP: {timestamp}")

# Check if lock exists
if os.path.exists(lock_path):
    print("LOCK EXISTS - another worker is operating")
    sys.exit(1)

# Create lock
with open(lock_path, "w") as f:
    f.write(f"{my_claim} | {timestamp}")
print("Lock acquired")

try:
    # Read queue
    with open(queue_path, "r") as f:
        queue = yaml.safe_load(f)

    # Find first AVAILABLE with completed_at:null
    target_idx = None
    for i, task in enumerate(queue.get("tasks", [])):
        if task.get("status") == "AVAILABLE" and task.get("completed_at") is None:
            # Also check claimed_by should be null or expired
            claimed_by = task.get("claimed_by")
            claimed_at = task.get("claimed_at")
            if claimed_by is None:
                target_idx = i
                break
            # Check if claim expired (300 seconds)
            if claimed_at:
                try:
                    claimed_time = datetime.fromisoformat(
                        claimed_at.replace("Z", "+00:00")
                    )
                    current_time = datetime.now()
                    seconds_since = (current_time - claimed_time).total_seconds()
                    if seconds_since > 300:  # expired
                        print(
                            f"Ticket {task['ticket_id']} has expired claim, will claim"
                        )
                        target_idx = i
                        break
                except:
                    # If can't parse, treat as available
                    target_idx = i
                    break

    if target_idx is None:
        print("No valid AVAILABLE task found")
        # Count CLAIMED tasks
        claimed_count = sum(
            1
            for t in queue.get("tasks", [])
            if t.get("status") in ["CLAIMED", "ACTIVE"]
        )
        print(f"CLAIMED tasks: {claimed_count}")
        if claimed_count > 0:
            print("FILA OCUPADA  {claimed_count} workers ativos.")
        else:
            print("All tasks DONE or inconsistent")
        sys.exit(1)

    # Make claim
    task = queue["tasks"][target_idx]
    print(f"Claiming ticket: {task['ticket_id']} - {task['title']}")

    queue["tasks"][target_idx]["claimed_by"] = my_claim
    queue["tasks"][target_idx]["claimed_at"] = timestamp
    queue["tasks"][target_idx]["status"] = "CLAIMED"

    # Write back
    with open(queue_path, "w") as f:
        yaml.dump(queue, f, default_flow_style=False, sort_keys=False)

    print("Claim successful")

except Exception as e:
    print(f"Error: {e}")
    import traceback

    traceback.print_exc()
finally:
    # Release lock
    if os.path.exists(lock_path):
        os.remove(lock_path)
        print("Lock released")
