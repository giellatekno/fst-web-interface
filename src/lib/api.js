const API_URLS = {
    divvun: "https://api-giellalt.uit.no/",
    local: "http://localhost:8000/",
};

const service_unavailable = new Response(null, {
    status: 503,
    statusText: "Service Unavailable",
});

async function apicall(url, { api = "divvun", json_body, method = "GET" } = {}) {
    if (!Object.hasOwn(API_URLS, api)) {
        throw new Error("Internal: bad call to apicall(): no such api");
    }

    url = API_URLS[api] + url;
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

    const response = await apicall(`hyphenate/${lang}/${word}`, {
        api: "local",
    });
    if (response.status !== 200) {
        console.error("hyphenation api error");
        console.error(response.statusText);
        throw new Error("hypenation api error");
    }

    const json = await response.json();
    return json.result;
}

export async function transcribe(lang, word) {
    if (!word) {
        throw new Error("ValueError: word must be non-empty");
    }

    const response = await apicall(`transcribe/${lang}/${word}`, {
        api: "local",
    });

    if (response.status !== 200) {
        console.error("transcribe api error");
        console.error(response.statusText);
        throw new Error("transcribe api error");
    }

    const json = await response.json();
    return json.result;
}

export async function disambiguate(lang, input) {
    if (!input) {
        throw new Error("ValueError: Bad internal call. api::disambiguate() given input must be non-empty");
    }

    const response = await apicall(
        `disambiguate/${lang}/${input}`,
        { api: "local" },
    );

    if (response.status !== 200) {
        console.error("api::disambiguate(), non 200 from api");
        console.error(response.statusText);
        throw new Error("api::disambiguate() error");
    }

    const json = await response.json();
    return json.result;
}
