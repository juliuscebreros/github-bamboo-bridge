#!/usr/bin/env python

import github3, sys, argparse, shutil
from git import Repo


def main( argv ):
    parser = argparse.ArgumentParser(
        description='Checkout a pull request, merge the fork'
    )
    parser.add_argument( '--api-user', required=True, help='Github User that will access the github api' )
    parser.add_argument( '--api-key', required=True, help='Github User personal access token to authenticate' )
    parser.add_argument( '--upstream-user', required=True, help='The owner of the repo to merge to' )
    parser.add_argument( '--repo-name', required=True, help='The name of the repo to merge to' )
    parser.add_argument( '--pr-number', required=True, help='The pull request number' )
    parser.add_argument( '--results-url', required=True, help='The bamboo results url' )

    args = parser.parse_args()

    API_USER = args.api_user
    API_KEY = args.api_key

    UPSTREAM_USER = args.upstream_user
    REPO_NAME = args.repo_name
    PULL_REQUEST = args.pr_number

    RESULTS_URL = args.results_url

    # Clean repo folder
    shutil.rmtree( "./project", ignore_errors=True )

    # Login to github
    gh = github3.login( API_USER, API_KEY )
    write_status_file( 'pending' )

    # Get upstream and fork
    upstream = gh.repository( UPSTREAM_USER, REPO_NAME )
    pr = upstream.pull_request( PULL_REQUEST )

    base_branch = pr.base.ref;

    print( "Merging into: " + pr.base.label + " from: " + pr.head.label );
    print( "PR Title: " + pr.title.encode('utf-8') )
    print( "Description: "+ pr.body.encode('utf-8') )

    # Check if safe to merge
    if pr.mergeable :
        # Clone repo
        g = Repo.clone_from( 'https://{0}:{1}@github.com/{2}.git'.format( API_USER, API_KEY, upstream.full_name), 'project', branch=base_branch)
        repo = 'https://{0}:{1}@github.com/{2}.git'.format( API_USER, API_KEY, pr.head._json_data[ 'repo' ][ 'full_name' ] )
        label = pr.head.ref

        print( u"Pulling from {0}".format( repo ) )
        print( "SHA: {0}".format( pr.head.sha ) )
        fork_g = g.create_remote( 'fork', repo )
        fork_g.pull( label )

        upstream.create_status(
            sha=pr.head.sha,
            target_url=RESULTS_URL,
            state='pending',
            description='Running tests',
            context='Bamboo'
        )

        write_status_file( 'pending' )
        return 0
    else :
        print( 'Not safe to merge' )
        write_status_file( 'failed' )
        return 1

def write_status_file( status ):
    f = open( './buildresult', 'w' )
    f.write( status )
    f.close()
    return

if __name__ == "__main__":
    sys.exit(main(sys.argv))
