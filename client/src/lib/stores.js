import {
    writable,
    derived,
} from "svelte/store";

import { locale } from "./locales.js";
import { language_names } from "./langs.js";

export const page_pathname = writable(
    new URL(window.location).pathname
);

// The language code of the language the user is exploring
export const lang = derived(
    page_pathname,
    $pn => $pn.split("/")[1]
);

// Which tool the user is exploring
export const tool = derived(
    page_pathname,
    $pn => $pn.split("/")[2] ?? ""
);

// language name of the language the user is currently exploring,
// in the currently set locale
export const lang_in_locale = derived(
    [lang, locale],
    ([$lang, $locale]) => language_names[$locale][$lang]
);
