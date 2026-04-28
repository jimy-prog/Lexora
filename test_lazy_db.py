import sys
sys.path.append("/Users/jamshidmahkamov/Desktop/teacher_admin")
from master_database import SessionMaster, PlatformTenant
from database import get_tenant_engine

mdb = SessionMaster()
tenant = mdb.query(PlatformTenant).filter_by(slug="lexorademo").first()
# Actually slug was generated dynamically: base_slug + rand_suffix
tenant = mdb.query(PlatformTenant).order_by(PlatformTenant.id.desc()).first()
print("Found tenant:", tenant.slug, tenant.db_filename)

print("Triggering DB file generation...")
engine = get_tenant_engine(tenant.db_filename)
print("Engine created.")
