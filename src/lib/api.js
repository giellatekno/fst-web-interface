const DIVVUN_API_ROOT = "https://divvun.github.io/divvun-api/";

const service_unavailable = new Response(null, {
    status: 503,
    statusText: "Service Unavailable",
});

async function apicall(url, { json_body, method = "GET" } = {}) {
    url = DIVVUN_API_ROOT + url;
    let response;
    const opts = { method };

    if (json_body) {
        opts.headers = { "Content-Type": "application/json" },
        opts.body = JSON.stringify(json_body);
    }

    try {
        response = await fetch(url, opts);
    } catch (e) {
        console.error("apicall failed");
        console.error(e);
        return service_unavailable;
    }

}

async function spell(lang, word) {
    const response = await apicall(`speller/${lang}`, {
        json_body: { word }});
    if (response.status !== 200) {
        console.error("speller api error");
        console.error(response.statusText);
    }

    const json = await response.json();
    return json.results;
}
