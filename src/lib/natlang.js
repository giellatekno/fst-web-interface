import {
    tool_langs,
    ui_langs,
} from "./config.js";

export const language_names = {};

for (const lang of ui_langs) {
    language_names[lang] = {};
    const lang_in = new Intl.DisplayNames(lang, { type: "language" });

    for (const other of tool_langs) {
        language_names[lang][other] = lang_in.of(other);
    }
}

