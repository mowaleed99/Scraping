"""
Recover ALL available posts from ALL Apify runs — no re-scraping needed.
"""
import asyncio
from apify_client import ApifyClientAsync
from app.core.config import get_settings
from app.db.session import get_db_session
from app.scraper.dedup import ingest_raw_posts
from sqlalchemy import select
from app.db.models.group import FacebookGroup


async def main():
    settings = get_settings()
    client = ApifyClientAsync(settings.apify_api_token)

    print("Fetching ALL Apify runs (no limit)...")
    # Fetch up to 100 runs, sorted newest first
    runs_page = await client.runs().list(desc=True, limit=100)
    all_runs = runs_page.items
    print(f"Found {len(all_runs)} total runs on Apify.")

    async with get_db_session() as session:
        stmt = select(FacebookGroup)
        groups = (await session.execute(stmt)).scalars().all()
        group_map = {g.group_id: g for g in groups}
        print(f"Groups in DB: {list(group_map.keys())}\n")

        total_inserted = 0
        seen_datasets = set()

        for run in all_runs:
            status = run.get("status")
            dataset_id = run.get("defaultDatasetId")
            run_id = run.get("id")

            # Include SUCCEEDED and ABORTED — aborted runs still have partial data in datasets
            if status not in ("SUCCEEDED", "ABORTED"):
                print(f"Run {run_id}: status={status}, skipping.")
                continue

            if not dataset_id or dataset_id in seen_datasets:
                print(f"Run {run_id}: duplicate or empty dataset, skipping.")
                continue

            seen_datasets.add(dataset_id)

            # Check how many items are in this dataset
            info = await client.dataset(dataset_id).get()
            item_count = info.get("itemCount", 0) if info else 0
            if item_count == 0:
                print(f"Run {run_id}: dataset {dataset_id} is empty, skipping.")
                continue

            # Peek at first item to detect which group it belongs to
            items_page = await client.dataset(dataset_id).list_items(limit=1)
            if not items_page.items:
                continue

            sample = items_page.items[0]
            url = (
                sample.get("url")
                or sample.get("facebookUrl")
                or sample.get("inputUrl")
                or ""
            )

            if "groups/" not in url:
                print(f"Run {run_id}: URL '{url}' is not a group URL, skipping.")
                continue

            fb_group_id = url.split("groups/")[1].split("/")[0].strip()
            group = group_map.get(fb_group_id)

            if not group:
                print(f"Run {run_id}: group {fb_group_id} not in DB, skipping.")
                continue

            print(
                f"Run {run_id}: recovering {item_count} posts "
                f"for group {group.group_name} ({fb_group_id})..."
            )

            async def stream_items(ds_id=dataset_id):
                async for item in client.dataset(ds_id).iterate_items():
                    yield item

            inserted = await ingest_raw_posts(session, group.id, None, stream_items())
            total_inserted += inserted
            print(f"  -> Inserted/updated {inserted} posts.\n")

        print(f"\n=== Done! Total posts recovered: {total_inserted} ===")


if __name__ == "__main__":
    asyncio.run(main())
