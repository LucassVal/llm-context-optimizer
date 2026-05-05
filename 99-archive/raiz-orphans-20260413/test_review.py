import sys

sys.path.insert(0, "01_neocortex_framework")
from neocortex.core.review import get_review_service
from pathlib import Path

handoff_path = Path("DIR-DS-002-audit-logs/NC-DS-034-handoff-20260413-010608.yaml")
print(f"Reviewing handoff: {handoff_path}")
service = get_review_service()
report = service.review(handoff_path)
print(f"Score: {report.score:.1f}/100")
print(f"Passed: {report.passed}")
print(f"Summary: {report.summary}")
print("Validator results:")
for result in report.validator_results:
    print(
        f"  {result.validator_name}: {result.passed} ({result.score:.2f}) - {result.message}"
    )
if report.recommendations:
    print("Recommendations:")
    for rec in report.recommendations:
        print(f"  - {rec}")
else:
    print("No recommendations.")
