#!/usr/bin/env python

from anytree import AnyNode, NodeMixin, RenderTree
from github import Github
from github import Auth
import argparse
import os

try:
    AUTH = Auth.Token(os.environ['GITHUB_ACCESS_TOKEN'])
except KeyError:
    AUTH = None

# ################
# ### Classes ####
# ################


class bcolors:
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'


class PullData(NodeMixin):
    def __init__(self,
                 title,
                 number,
                 base,
                 head,
                 labels,
                 is_merged,
                 html_url,
                 parent=None,
                 children=None):
        self.title = title
        self.number = number
        self.base = base
        self.head = head
        self.labels = labels
        self.is_merged = is_merged
        self.html_url = html_url
        self.parent = parent
        if children:
            self.children = children


# ##################
# ### Functions ####
# ##################

def print_tree(root, print_urls=False):
    for pre, fill, node in RenderTree(root):
        try:
            if node.number:
                if node.is_merged:
                    number = "%s%s%s" % (
                        bcolors.FAIL, node.number, bcolors.ENDC)
                else:
                    number = "%s%s%s" % (
                        bcolors.OKGREEN, node.number, bcolors.ENDC)
                title = "%s%s%s" % (bcolors.OKBLUE, node.title, bcolors.ENDC)
                head = "%s%s%s" % (bcolors.WARNING, node.head, bcolors.ENDC)
                base = "%s%s%s" % (bcolors.OKCYAN, node.base, bcolors.ENDC)
                url = "%s%s%s" % (bcolors.ENDC, node.html_url, bcolors.ENDC)
                pr_line = "%s%s %s [%s -> %s]" % (pre, number,
                                                  title.ljust(98-len(pre)),
                                                  head, base)
                print(pr_line)
                if print_urls:
                    url_line = "%s%s" % (fill, url)
                    print(url_line)
            else:
                pr_line = "%s%s" % (pre, title)
                print(pr_line.ljust(8))
        except AttributeError:
            pass


def main(args):
    tree_root = AnyNode(title="Pull Requests for %s" % (args.repository))
    branch_pr_map = {}
    branch_pr_map["NLnetLabs:main"] = tree_root
    pull_requests = []

    with Github(auth=AUTH) as g:
        repo = g.get_repo("NLnetLabs/domain")
        #  repo = g.get_repo("NLnetLabs/dnst")
        for pull in repo.get_pulls():
            pull_requests.append(PullData(
                title=pull.title,
                number=pull.number,
                base=pull.base.label,
                head=pull.head.label,
                labels=pull.labels,
                is_merged=pull.merged,
                html_url=pull.html_url,
            ))

        for p in pull_requests:
            branch_pr_map[p.head] = p

        for p in pull_requests:
            p.parent = branch_pr_map[p.base]

    print_tree(tree_root, print_urls=args.urls)


if __name__ == '__main__':
    # Argument Parsing
    description = '''
GitHub PR Tree: Show a tree view of GitHub Pull Requests \
based on their merge targets.

Optionally takes a GitHub Access Token from the environment \
variable 'GITHUB_ACCESS_TOKEN' to have less strict rate limiting. \
This program only needs read-only access.
'''
    parser = argparse.ArgumentParser(
        prog='pr-tree',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=description,
        epilog='The API access is not yet optimized, '
        'and is therefore relatively slow.'
    )
    parser.add_argument(
        'repository', help="The repository (e.g. NLnetLabs/domain)")
    parser.add_argument('-u', '--urls',
                        help='Print URLs to the PRs', action='store_true')

    args = parser.parse_args()

    if args.repository.find('/') == -1:
        print("Error: The repository name needs to include the namespace, "
              "e.g. NLnetLabs/domain")
        exit(1)

    main(args)
