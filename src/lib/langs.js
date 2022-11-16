import { locales } from "./locales.js";

// an object of objects, where the idea is that you
// can find out
//   "how do I say 'northern sami' in 'norwegian'"
// by looking for `language_names["nob"]["sme"]`
export const language_names = {};

export const langs = [
    "bxr",
    "chr",
    "ciw",
    "cor",
    "crk",
    "deu",
    "est",
    "evn",
    "fao",
    "fin",
    "fit",
    "fkv",
    "gle",
    "hdn",
    "hun",
    "ipk",
    "izh",
    "kal",
    "kca",
    "koi",
    "kom",
    "kpv",
    "lav",
    "liv",
    "lut",
    "mdf",
    "mhr",
    "mns",
    "mrj",
    "myv",
    "nio",
    "nno",
    "nob",
    "olo",
    "rmf",
    "rup",
    "rus",
    "sjd",
    "sje",
    "sma",
    "sme",
    "smj",
    "smn",
    "sms",
    "som",
    "swe",
    "udm",
    "vep",
    "vot",
    "vro",
    "yrk",
];

const all_langs = new Set([
    "bxr", "ciw", "cor", "est", "evn",
    "fao", "fin", "fit", "fkv", "gle",
    "hdn", "ipk", "izh", "kal", "kca",
    "koi", "kpv", "liv", "mdf", "mhr",
    "mns", "mrj", "myv", "nio", "nob",
    "olo", "rmf", "rus", "sjd", "sje",
    "sma", "sme", "smj", "smn", "sms",
    "som", "udm", "vep", "vot", "vro",
    "yrk",
]);

export const analysis_langs = new Set(all_langs);

export const paradigm_langs = new Set([
    "bxr", "ciw", "cor", "evn", "fao",
    "fin", "fit", "fkv", "gle", "ipk",
    "izh", "kal", "kca", "koi", "kpv",
    "liv", "mdf", "mhr", "mns", "mrj",
    "myv", "nio", "nob", "olo", "rus",
    "sjd", "sje", "sma", "sme", "smj",
    "smn", "sms", "som", "udm", "vep",
    "vot", "vro", "yrk",
]);

export const generation_langs = new Set([
    "bxr", "ciw", "cor", "est", "evn",
    "fao", "fin", "gle", "hdn", "ipk",
    "izh", "kal", "kca", "koi", "kpv",
    "liv", "mdf", "mhr", "mns", "mrj",
    "myv", "nio", "nob", "olo", "rus",
    "sjd", "sje", "sma", "sme", "smj",
    "smn", "sms", "som", "udm", "vep",
    "vot", "vro", "yrk",
]);

export const num_langs = new Set([
    "fin", "hdn", "liv", "mdf", "mhr",
    "myv", "olo", "rus", "sjd", "sma",
    "sme", "smj", "smn", "sms", "yrk",
]);

for (const locale of locales) {
    language_names[locale] = {};

    const lang_in = new Intl.DisplayNames(
        locale, { type: "language" });

    for (const lang of langs) {
        language_names[locale][lang] = lang_in.of(lang);
    }
}

export const lang_star = {
    "sme": "gold",
    "fin": "gold",
    "sms": "gold",
    "sma": "gold",
    "mdf": "gold",
    "bxr": "gold",
    "chr": "gold",
    "ciw": "silver",
    "cor": "silver",
    "crk": "silver",
    "deu": "silver",
    "est": "silver",
    "evn": "silver",
    "fao": "silver",
    "fit": "silver",
    "fkv": "silver",
    "gle": "silver",
    "hdn": "silver",
    "hun": "silver",
    "ipk": "bronze",
    "izh": "bronze",
    "kal": "bronze",
    "kca": "bronze",
    "koi": "bronze",
    "kom": "bronze",
    "kpv": "bronze",
    "lav": "bronze",
    "liv": "bronze",
    "lut": "bronze",
    "mhr": "bronze",
    "mns": "bronze",
    "mrj": "bronze",
    "myv": "bronze",
    "nio": "bronze",
    "nno": "bronze",
    "nob": "bronze",
    "olo": "bronze",
    "rmf": "bronze",
    "rup": "bronze",
    "rus": "bronze",
    "sjd": "bronze",
    "sje": "bronze",
    "smj": "bronze",
    "smn": "bronze",
    "som": "bronze",
    "swe": "bronze",
    "udm": "bronze",
    "vep": "bronze",
    "vot": "bronze",
    "vro": "bronze",
    "yrk": "bronze",
}
