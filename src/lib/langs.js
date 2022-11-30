import { locales } from "./locales.js";

// an object of objects, where the idea is that you
// can find out
//   "how do I say 'northern sami' in 'norwegian'"
// by looking for `language_names["nob"]["sme"]`
export const language_names = {};

const all_langs = [
    "bxr", "chr", "ciw", "cor", "crk",
    "deu", "est", "evn", "fao", "fin",
    "fit", "fkv", "gle", "hdn", "hun",
    "ipk", "izh", "kal", "kca", "koi",
    "kom", "kpv", "lav", "liv", "lut",
    "mdf", "mhr", "mns", "mrj", "myv",
    "nio", "nno", "nob", "olo", "rmf",
    "rup", "rus", "sjd", "sje", "sma",
    "sme", "smj", "smn", "sms", "som",
    "swe", "udm", "vep", "vot", "vro",
    "yrk",
];

export const langs = [
    "bxr", "ciw", "cor", "est", "evn",
    "fao", "fin", "fit", "fkv", "gle",
    "hdn", "ipk", "izh", "kal", "kca",
    "koi", "kpv", "liv", "mdf", "mhr",
    "mns", "mrj", "myv", "nio", "nob",
    "olo", "rmf", "rus", "sjd", "sje",
    "sma", "sme", "smj", "smn", "sms",
    "som", "udm", "vep", "vot", "vro",
    "yrk",
];

export const sami_langs = new Set([
    "sjd", "sje", "sma", "sme", "smj", "smn", "sms",
]);

export const nonsamiuralic_langs = new Set([
    "myv", "est", "fin", "mrj", "izh", "rmf", "kca",
    "kpv", "koi", "fkv", "liv", "olo", "mns", "fit", "mdf",
    "yrk", "nio", "udm", "vep", "vro", "vot", "mhr",
]);

export const other_langs = new Set([
    "bxr", "evn", "fao", "kal", "gle", "ipk", "cor",
    "hdn", "nno", "nob", "ciw", "crk", "rus", "som",
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

