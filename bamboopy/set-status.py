#!/usr/bin/env python

import github3, sys, argparse, shutil

def main( argv ):
    parser = argparse.ArgumentParser(
        description='Set pull request status based on results'
    )
    parser.add_argument( '--api-user', required=True, help='Github User that will access the github api' )
    parser.add_argument( '--api-key', required=True, help='Github User personal access token to authenticate' )
    parser.add_argument( '--upstream-user', required=True, help='The owner of the repo to merge to' )
    parser.add_argument( '--repo-name', required=True, help='The name of the repo to merge to' )
    parser.add_argument( '--pr-number', required=True, help='The pull request number' )
    parser.add_argument( '--results-url', required=True, help='The Bamboo results url' )

    args = parser.parse_args()

    API_USER = args.api_user
    API_KEY = args.api_key
    UPSTREAM_USER = args.upstream_user
    REPO_NAME = args.repo_name
    PR_NUMBER = args.pr_number

    RESULTS_URL = args.results_url;

    f = open( './buildresult', 'r' )
    val = f.read()

    # Login to github
    gh = github3.login( API_USER, API_KEY )
    upstream = gh.repository( UPSTREAM_USER, REPO_NAME )
    pr = upstream.pull_request( PR_NUMBER )

    updateStatus(  upstream, pr, val )
    return

def updateStatus( repo, pr, status ):
    print( 'Setting status: {0}'.format( status ) )
    if status == 'success':
        repo.create_status(
            sha=pr.head.sha,
            target_url=RESULTS_URL
            state='success',
            description='Build successful',
            context='Bamboo'
        )
    else:
        repo.create_status(
            sha=pr.head.sha,
            target_url=RESULTS_URL
            state='failure',
            description='Build failed',
            context='Bamboo'
        )

    return

if __name__ == "__main__":
    main(sys.argv)
