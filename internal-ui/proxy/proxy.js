import * as http from 'http';
import axios from 'axios';

if (!process.env.session) {
    console.error(`session env was not defined.\nFetch your session from: https://internal.console.stage.redhat.com/api/turnpike/session/\nand set as an env variable for this proxy to work.`);
    process.exit(2);
}

const logResponse = (url, method, response) => {
    console.log(`Fetching ${method} ${url}: Response status: ${response.status}`);
}

http.createServer(async function (req, res) {
    const sessionCookie = `session=${process.env.session}`;
    const cookies = (req.headers['cookie'] ?? '') + `; ${sessionCookie}`;
    const base = 'https://internal.console.stage.redhat.com';
    const path = req.url.replace(/^\/api\/v1/, '/api/virtual-assistant/v1');
    const url = `${base}${path}`
    const method = req.method;

    try {
        const response = await axios.request(
            {
                url: url,
                method: method,
                proxy: {
                    protocol: 'http',
                    host: 'squid.corp.redhat.com',
                    port: 3128
                },
                headers: {
                    Cookie: cookies
                },
                transformResponse: res => res
            }
        );

        logResponse(url, method, response);

        res.writeHead(response.status, response.headers);
        res.end(response.data);
    } catch (e) {
        logResponse(url, method, e.response);
        res.writeHead(e.response.status, e.response.headers);
        res.end(e.response.data);
    }
}).listen(8083);
