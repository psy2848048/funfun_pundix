from crawl import SteemPosting
import sys

if __name__ == "__main__":
    st = SteemPosting()
    permlinks = st.getRecentPaidOutPostPermlinks()
    if len(permlinks) < 1:
        sys.exit(0)

    filtered_permlinks = st.getValidPermlinks(permlinks)
    if len(filtered_permlinks) < 1:
        sys.exit(0)

    sys.exit(1)
