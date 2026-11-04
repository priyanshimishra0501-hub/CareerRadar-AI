
from services.job_fetcher import fetch_all_jobs
from services.database import save_jobs, get_all_jobs


def main():

    print("\n" + "=" * 50)
    print("       CAREERRADAR AI - JOB IMPORT")
    print("=" * 50)

    # Step 1: Fetch real opportunities
    jobs = fetch_all_jobs()

    if not jobs:
        print("\nNo jobs fetched. Check your internet/API connection.")
        return

    # Step 2: Save opportunities in SQLite
    inserted, updated = save_jobs(jobs)

    # Step 3: Read stored opportunities
    all_jobs = get_all_jobs()

    print("\n" + "=" * 50)
    print("             IMPORT SUMMARY")
    print("=" * 50)

    print(f"New opportunities saved : {inserted}")
    print(f"Existing jobs updated   : {updated}")
    print(f"Total jobs in database  : {len(all_jobs)}")

    print("\nLATEST OPPORTUNITIES")
    print("-" * 50)

    for index, job in enumerate(all_jobs[:10], start=1):

        print(f"\n{index}. {job['title']}")
        print("Company :", job['company'])
        print("Location:", job['location'])
        print("Source  :", job['source'])
        print("Apply   :", job['url'])

    print("\n" + "=" * 50)
    print("CareerRadar AI import completed!")
    print("=" * 50)


if __name__ == "__main__":
    main()

