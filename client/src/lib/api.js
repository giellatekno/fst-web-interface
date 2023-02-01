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

async function apicall(
    url,
    {
        method = "GET",
        api = "divvun",
        json_body,

        // assume root output from api is an object, and extract this key
        // for the results
        extract = "result",
    } = {}
) {
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

    if (!extract) {
        return json;
    } else {
        const result = json.result;
        if (result === undefined) {
            const e = json.error || json.errors || "no 'result' nor 'error' in json body";
            throw new Error(e);
        }
        return result;
    }
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

const PARADIGM_SIZES = ["min", "standard", "full"];
const WORD_CLASSES = ["Any", "N", "A", "V", "Adv", "Adj", "Pron", "Num"];
export async function paradigm(lang, input, wordclass_idx, size_idx) {
    check_arg_nonempty("paradigm", input, "input");

    const word_class = WORD_CLASSES[wordclass_idx];
    const mode = PARADIGM_SIZES[size_idx];

    const query_params = new URLSearchParams({ word_class, mode }).toString();

    return apicall(`paradigm/${lang}/${input}?${query_params}`, { api: "local" });
}

export async function dependency(lang, input) {
    check_arg_nonempty("dependency", input, "input");

    return apicall(`dependency/${lang}/${input}`, { api: "local" });
}

export async function num(lang, input) {
    check_arg_nonempty("num", input, "input");

    return apicall(`num/${lang}/${input}`, { api: "local" });
}

export async function capabilities_for_lang(lang) {
    check_arg_nonempty("capabilities_for_lang", lang, "lang");

    return apicall(`capabilities/${lang}`, { api: "local", extract: false });
}
