const DIVVUN_API_ROOT = "https://api-giellalt.uit.no/";

const service_unavailable = new Response(null, {
    status: 503,
    statusText: "Service Unavailable",
});

async function apicall(url, { json_body, method = "GET" } = {}) {
    url = DIVVUN_API_ROOT + url;
    const opts = { method };

    if (json_body) {
        opts.mode = "cors";
        opts.method = "POST";
        opts.headers = { "Content-Type": "application/json" },
        opts.body = JSON.stringify(json_body);
    }

    let response;
    try {
        response = await fetch(url, opts);
    } catch (e) {
        return service_unavailable;
    }

    return response;
}

export async function spell(lang, word) {
    if (!word) {
        throw new Error("ValueError: word must be non-empty");
    }

    if (lang === "sme") {
        // se = swedish ?
        lang = "se";
    }

    const response = await apicall(`speller/${lang}`, {
        json_body: { text: word }});
    if (response.status !== 200) {
        console.error("speller api error");
        console.error(response.statusText);
        throw new Error("speller api error");
    }

    const json = await response.json();
    return json.results;
}

export async function hyphenate(lang, word) {
    if (!word) {
        throw new Error("ValueError: word must be non-empty");
    }

    if (lang === "sme") {
        // se = swedish ?
        //lang = "se";
    }

    const response = await apicall(`hyphenation/${lang}`, {
        json_body: { text: word }});
    if (response.status !== 200) {
        console.error("hyphenation api error");
        console.error(response.statusText);
        throw new Error("hypenation api error");
    }

    const json = await response.json();
    return json.results;
}
