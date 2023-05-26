import requests
from datetime import datetime


def get_closed_issues_after_release(repo_owner, repo_name, release_date):
    closed_issues = []

    page = 1

    url = f'https://api.github.com/repos/{repo_owner}/{repo_name}/issues'

    while True:
        params = {
            'state': 'closed',
            'since': release_date.isoformat(),
            'per_page': 100,
            'page': page,
        }
        response = requests.get(url, params=params)

        if response.status_code != 200:
            print(f"Error: {response.status_code} {response.text}")
            break

        issues = response.json()

        if not issues:
            break

        for issue in issues:
            if 'pull_request' not in issue:
                if 'Feature' in issue['title']:
                    closed_issues.append(
                        "Implemented: [" + issue['title'] + " " + str(issue['number']) + "](" + issue['html_url'] + ")")
                if 'Bug' in issue['title']:
                    closed_issues.append(
                        "Fixed: [" + issue['title'] + " " + str(issue['number']) + "](" + issue['html_url'] + ")")

        page += 1

    return closed_issues


def get_merged_prs_after_release(repo_owner, repo_name, release_date):
    merged_prs = []
    base_url = f'https://api.github.com/search/issues'
    page = 1
    per_page = 100

    # Convert release_date to ISO 8601 format
    release_date_iso = release_date.isoformat()

    while True:
        query = f'repo:{repo_owner}/{repo_name} type:pr is:merged merged:>{release_date_iso}'
        params = {
            'q': query,
            'sort': 'updated',
            'order': 'desc',
            'page': page,
            'per_page': per_page,
        }

        response = requests.get(base_url, params=params)
        if response.status_code != 200:
            print(f"Error: {response.status_code} {response.text}")
            break

        search_result = response.json()
        prs = search_result.get('items', [])

        if not prs:
            break

        for pr in prs:
            if pr['user']['login'] == 'dependabot[bot]':
                continue
            summary = f"PR title: {pr['title']}\nPR summary: {pr['body']}\n"
            merged_prs.append(summary)
        page += 1

    return merged_prs


def get_release_data(repo_owner, repo_name, release_tag):
    releases_url = f'https://api.github.com/repos/{repo_owner}/{repo_name}/releases'
    releases_response = requests.get(releases_url)
    releases_data = releases_response.json()

    if not isinstance(releases_data, list):
        print("Error: Unexpected API response:", releases_data)
        print("might exceed rate limit")
        return None

    for release in releases_data:
        if release['tag_name'] == release_tag:
            return release

    return None


def main():
    release_url = input("Enter the GitHub the previous release URL: ").strip()
    while True:
        is_breaking_change = input(
            "is the new release going to be a breaking change? [y/n]: ").strip()
        if is_breaking_change == 'y' or is_breaking_change == 'n':
            if is_breaking_change == 'y':
                is_breaking_change = True
                break
            if is_breaking_change == 'n':
                is_breaking_change = False
                break
        else:
            print("Invalid input. Please enter 'y' or 'n'.")

    repo_owner, repo_name = release_url.split('/')[-5:-3]
    release_tag = release_url.split('/')[-1]

    release_data = get_release_data(repo_owner, repo_name, release_tag)

    if not release_data:
        print("Unable to find the release.")
        return

    if 'created_at' in release_data:
        release_date_str = release_data['created_at']
        release_date = datetime.fromisoformat(
            release_date_str.replace("Z", "+00:00"))
        print("release date is: ", release_date)
    else:
        print("Unable to find the release date.")
        return

    closed_issues = get_closed_issues_after_release(
        repo_owner, repo_name, release_date)
    merged_prs = get_merged_prs_after_release(
        repo_owner, repo_name, release_date)

    with open('summary.txt', 'w') as f:
        if is_breaking_change:
            f.write("❗️⚠️ BREAKING CHANGE ⚠️❗️\n")
            f.write("what needs to be wiped???\n")

        f.write("\n## What's New\n")
        f.write("\nissues:\n")
        for issue in closed_issues:
            f.write(issue + '\n')
        f.write("\npr's:\n")
        for pr in merged_prs:
            f.write(pr + '\n')

        # Append the static version explanation
        f.write(
            "\nThere are two [versions](https://en.wikipedia.org/wiki/X86-64#Microarchitecture_levels):\n")
        f.write("- x86-64-v3: for newer processors since ~2015\n")
        f.write("- x86-64-v2: for older processors since ~2009 and some old VMs\n")

    file = open('summary.txt', 'r')
    contents = file.read()
    print(contents)
    file.close()


if __name__ == '__main__':
    main()
