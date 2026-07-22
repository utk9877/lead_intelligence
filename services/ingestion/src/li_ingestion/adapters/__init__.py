from li_ingestion.adapters.base import Adapter, AdapterResult
from li_ingestion.adapters.careers_pages import CareersPagesAdapter
from li_ingestion.adapters.job_boards import JobBoardsAdapter
from li_ingestion.adapters.news_funding import NewsFundingAdapter
from li_ingestion.adapters.registry_gst import RegistryGstAdapter
from li_ingestion.adapters.registry_mca import RegistryMcaAdapter
from li_ingestion.adapters.site_tech import SiteTechAdapter

__all__ = [
    "Adapter",
    "AdapterResult",
    "CareersPagesAdapter",
    "JobBoardsAdapter",
    "NewsFundingAdapter",
    "RegistryGstAdapter",
    "RegistryMcaAdapter",
    "SiteTechAdapter",
]
