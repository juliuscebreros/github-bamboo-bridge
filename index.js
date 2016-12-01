const restify = require( 'restify' );
const bamboo = require( './bamboo' );
const crypto = require( 'crypto' );
const bufferEq = require( 'buffer-equal-constant-time' );

// load environment variables using dotenv
require( 'dotenv' ).config();

// make sure github signature is valid
function signBlob( key, blob ) {
    return `sha1=${crypto.createHmac( 'sha1', key ).update( blob ).digest( 'hex' )}`;
}

// ==========  Restify Server ============= //
const server = restify.createServer( {
    name: 'GithubBambooBridge'
} );


server.use( restify.bodyParser( { mapParams: false } ) );
server.use( restify.queryParser() );

server.post(
    '/pullrequest/:buildId',
    ( req, res, next ) => {
        const sig = req.headers[ 'x-hub-signature' ];
        const event = req.headers[ 'x-github-event' ];
        const id = req.headers[ 'x-github-delivery' ];

        if ( !sig ) {
            return next( new restify.errors.BadRequestError( 'No X-Hub-Signature found on request' ) );
        }

        if ( !event ) {
            return next( new restify.errors.BadRequestError( 'No X-Github-Event found on request' ) );
        }

        if ( !id ) {
            return next( new restify.errors.BadRequestError( 'No X-Github-Delivery found on request' ) );
        }

        if ( event !== 'pull_request' ) {
            return next( new restify.errors.BadRequestError( 'Not a pull request event' ) );
        }

        const computedSig = new Buffer( signBlob( process.env.SECRET_KEY, JSON.stringify( req.body ) ) );

        if ( !bufferEq( new Buffer( sig ), computedSig ) ) {
            return next( new restify.errors.BadRequestError( 'X-Hub-Signature does not match blob signature' ) );
        }

        const pullRequest = req.body;
        const buildId = req.params.buildId;

        if ( pullRequest.action === 'closed' && pullRequest.pull_request.merged ) {
            res.send( 204 );
        } else {
            bamboo.queueBuild( buildId, pullRequest.number )
                .then( ( body ) => {
                    res.send( body );
                } )
                .catch( ( err ) => {
                    console.error( err );
                    res.send( 400, err );
                } );
        }

        return next();
    } );

server.get( '/', ( req, res, next ) => {
    res.send( 200, 'I\'m up' );
    return next();
} );

server.listen( process.env.PORT, () => {
    console.log( `Listening at port ${process.env.PORT}` );
} );

// ***************  Restify Server **************  //
