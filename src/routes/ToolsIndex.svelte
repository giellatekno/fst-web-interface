<script>
    import example_img from "../assets/language.svg";
    import spellcheck_img from "../assets/spellcheck.svg";
    import hyphenation_img from "../assets/hyphenation.svg";
    import num_img from "../assets/num.svg";
    import ipa_img from "../assets/ipa.svg";
    import { t } from "svelte-intl-precompile";
    import { locale } from "../lib/locales.js";
    import { capabilities_for_lang } from "../lib/api.js";
    import {
        lang,
        lang_in_locale,
    } from "../lib/stores.js";
    import {
        language_names,
        tools_for
    } from "../lib/langs.js";

    function get_copyright($t, $lang) {
        const specific_key = `copyright.lang.${$lang}`;
        const specific_value = $t(specific_key);
        if (specific_value !== specific_key) {
            return specific_value;
        } else {
            const generic_key = `copyright`;
            const generic_value = $t(generic_key);
            if (generic_value !== generic_key) {
                return generic_value;
            } else {
                // ??
                return "";
            }
        }
    }

    const IMAGES = {
        spellcheck: spellcheck_img,
        hyphenation: hyphenation_img,
        num: num_img,
        transcription: ipa_img,
    }

    let repo_info = null;
    let show_date_relative = false;
    $: get_repo_info($lang);
    $: repo_date = fmt_date_localized($locale, repo_info);
    $: repo_date_ago = fmt_date_ago_localized($locale, repo_info);

    $: copyright = get_copyright($t, $lang);
    $: tools = tools_for[$lang];


    const FMT_DATE_OPTS = { day: "numeric", month: "short", year: "numeric" };
    const RELTIME_FMT_OPTS = { };
    // https://blog.webdevsimplified.com/2020-07/relative-time-format/
    const DIVISIONS = [
        { amount: 60, name: 'seconds' },
        { amount: 60, name: 'minutes' },
        { amount: 24, name: 'hours' },
        { amount: 7, name: 'days' },
        { amount: 4.34524, name: 'weeks' },
        { amount: 12, name: 'months' },
        { amount: Number.POSITIVE_INFINITY, name: 'years' },
    ];
    function fmt_date_ago_localized(locale, date) {
        if (!date) return null;
        date = date.date;
        let diff_sec = (date - Date.now()) / 1000;

        const formatter = new Intl.RelativeTimeFormat(locale, RELTIME_FMT_OPTS);
        for (let i = 0; i <= DIVISIONS.length; i++) {
            const division = DIVISIONS[i]
            if (Math.abs(diff_sec) < division.amount) {
                return formatter.format(Math.round(diff_sec), division.name)
            }
            diff_sec /= division.amount
        }
    }
    function fmt_date_localized(locale, date) {
        if (!date) return null;
        date = date.date;
        return date.toLocaleDateString(locale, FMT_DATE_OPTS);
    }
    async function get_repo_info(lang) {
        if (!lang) throw Error();
        const obj = await capabilities_for_lang(lang);
        if (!obj.commit) throw Error();
        obj.date = new Date(obj.date);
        repo_info = obj;
    }
</script>

<main>
    <h2>{$t("lt")} {$t(`lname.lang.${$lang}`)}</h2>

    <div class="tools-wrapper">
        {#each tools as tool}
            <a href="/{$lang}/{tool}" class="tool">
                <img src={IMAGES[tool] || example_img} alt="">
                <span class="title">{$t(tool)}</span>
                <span class="desc">
                    {@html $t(tool + ".description")}
                </span>
            </a>
        {/each}
    </div>

    <p>
        Andre ressurser for {$lang_in_locale}
    </p>

    <a href="#">Direktelenke for denne siden</a>

    {#if repo_info}
        <div style="margin-top: 3em;">
            <p class="langmodel-info">
                {$t("langmodellastupdated")}
                <span class="date" on:click={() => show_date_relative = !show_date_relative}>
                    {show_date_relative ? repo_date_ago : repo_date}
                </span>&mdash;&nbsp;<code>commit {repo_info.commit},
                    <a rel="external" href="https://github.com/giellalt/lang-{$lang}"
                    >github.com/giellalt/lang-{$lang}</a></code>
            </p>
        </div>
    {/if}

    <p>{@html copyright}</p>
</main>


<style>
    main {
        margin-left: 34px;
    }

    span.date {
        cursor: pointer;
        border-bottom: 1px dashed black;
    }

    div.tools-wrapper {
        display: grid;
        grid-template-columns: repeat(2, max-content);
        grid-gap: 17px;
        /*width: calc(100vw - 68px);*/
    }

    @media screen and (max-width: 768px) {
        div.tools-wrapper {
            grid-template-columns: 1fr;
        }
    }

    a.tool { 
        display: grid;
        color: black;
        text-decoration: none;
        grid-template-areas:
            'img img title title title'
            'img img desc desc desc';
        grid-template-columns: 35px 35px repeat(3, max-content);
        background-color: #f0e89e;
        border-radius: 4px;
        padding: 4px 12px;
        box-shadow: 2px 2px 4px 0px rgba(121, 121, 89, 0.44);
        transition:
            background-color ease-out 0.25s;
    }

    @media screen and (max-width: 768px) {
        a.tool {
        }
    }

    a.tool:hover {
        background-color: #ece268;
    }

    a.tool > img {
        align-self: center;
        grid-area: img;
        height: 68px;
        width: 68px;
    }

    a.tool > span.title {
        margin-left: 10px;
        justify-self: start;
        align-self: end;
        grid-area: title;
        font-size: 1.6em;
        font-weight: 500;
        font-variant: small-caps;
        margin-bottom: 6px;
    }

    a.tool > span.desc {
        margin-left: 12px;
        justify-self: start;
        align-self: start;
        grid-area: desc;
        font-style: italic;
        font-size: 1.05em;
    }

    p.langmodel-info {
        display: inline;
        font-size: 0.85em;
        padding: 8px 10px;
        border: 2px solid #d9d914;
        background-color: #f4f49c;
    }

    p.langmodel-info,
    p.langmodel-info a,
    p.langmodel-info code {
        color: #111;
    }
</style>
