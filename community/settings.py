
# Fallback for direct execution from /community/interop.
from interop.bo import BO
from interop.bs import BS

from iop import Production

prod = (
    Production("Python.Production", testing_enabled=True)
    .actor_pool(1)
    .describe("Flask HTTP bridge to Python BO")
)

service = prod.service("BS", BS)
operation = prod.operation("BO", BO)
prod.connect(service.Output, operation)

PRODUCTIONS = [prod]