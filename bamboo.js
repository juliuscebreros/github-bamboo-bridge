const request = require( 'request-promise' );


module.exports = {
    queueBuild( buildId, prNumber ) {
        const username = process.env.BAMBOO_USER;
        const password = process.env.BAMBOO_PASSWORD;
        const port = process.env.BAMBOO_PORT;
        console.log( `Connecting to Bamboo as ${username}` );
        const options = {
            method: 'POST',
            uri: `http://${username}:${password}@localhost:${port}/rest/api/latest/queue/${buildId}`,
            json: true,
            qs: {
                os_authType: 'basic',
                'bamboo.variable.PR_NUMBER': prNumber
            }
        };

        return request( options );
    }
};
