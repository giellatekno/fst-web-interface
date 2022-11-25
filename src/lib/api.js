const API_URLS = {
    divvun: "https://api-giellalt.uit.no/",
    local: "http://localhost:8000/",
};

const service_unavailable = new Response(null, {
    status: 503,
    statusText: "Service Unavailable",
});

const check_arg_nonempty = (fnname, arg, argname) => {
    if (!arg) {
        throw new Error(`ValueError: Bad internal call. api::${fnname}() '${argname}' must be non-empty`);
    }
}

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

    if (response.status !== 200) {
        throw new Error(`non-200 when calling api (${url})`);
    }

    let json;
    try {
        json = await response.json();
    } catch (e) {
        throw new Error(`api response body not json (${url})`);
    }

    const results = json.result;
    if (results === undefined) {
        const e = json.error || json.errors || "no 'results' nor 'error' in json body";
        throw new Error(e);
    }
    return results;
}

export async function spell(lang, word) {
    check_arg_nonempty("spell", lang, "lang");

    if (lang === "sme") {
        // on divvun api, use 2-char for the langs that have a 2-char code,
        // else use 3-char.
        // on local: always 3-char
        lang = "se";
    }

    return apicall(`speller/${lang}`, { json_body: { text: word }});
}

export async function analyze(lang, word) {
    check_arg_nonempty("analyze", word, "word");

    return apicall(`analyze/${lang}/${word}`, { api: "local" });
}

export async function generate(lang, word) {
    check_arg_nonempty("generate", word, "word");

    return apicall(`generate/${lang}/${word}`, { api: "local" });
}

export async function hyphenate(lang, word) {
    check_arg_nonempty("hyphenate", word, "word");

    return apicall(`hyphenate/${lang}/${word}`, { api: "local" });
}

export async function transcribe(lang, word) {
    check_arg_nonempty("transcribe", word, "word");

    return apicall(`transcribe/${lang}/${word}`, { api: "local" });
}

export async function disambiguate(lang, input) {
    check_arg_nonempty("disambiguate", input, "input");

    return apicall(`disambiguate/${lang}/${input}`, { api: "local" });
}

export async function paradigm(lang, input) {
    check_arg_nonempty("paradigm", input, "input");

    return apicall(`paradigm/${lang}/${input}`, { api: "local" });
}

export async function dependency(lang, input) {
    check_arg_nonempty("dependency", input, "input");

    return apicall(`dependency/${lang}/${input}`, { api: "local" });
}

export async function num(lang, input) {
    check_arg_nonempty("num", input, "input");

    return apicall(`num/${lang}/${input}`, { api: "local" });
}
