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

    args = parser.parse_args()

    API_USER = args.api_user
    API_KEY = args.api_key

    UPSTREAM_USER = args.upstream_user
    REPO_NAME = args.repo_name
    PULL_REQUEST = args.pr_number

    # Clean repo folder
    shutil.rmtree( "./project", ignore_errors=True )

    # Login to github
    gh = github3.login( API_USER, API_KEY )

    # Get upstream and fork
    upstream = gh.repository( UPSTREAM_USER, REPO_NAME )
    pr = upstream.pull_request( PULL_REQUEST )

    print( "Testing PR {0}".format(pr.title) )
    print( "Description {0}".format( pr.body ) )

    # Check if safe to merge
    f = open( './buildresult', 'w' )
    if pr.mergeable :
        # Clone repo
        g = Repo.clone_from( upstream.clone_url, 'project')
        repo = pr.head._json_data[ 'repo' ][ 'clone_url' ]
        label = pr.head.ref

        print( "Pulling from {0}".format( repo ) )
        print( "SHA: {0}".format( pr.head.sha ) )
        fork_g = g.create_remote( 'fork', repo )
        fork_g.pull( label )

        upstream.create_status(
            sha=pr.head.sha,
            state='pending',
            description='Running tests',
            context='Bamboo'
        )

        f.write( 'pending' )
    else :
        print( 'Not safe to merge' )
        f.write( 'failed' )

    f.close()
    return

if __name__ == "__main__":
    main(sys.argv)
