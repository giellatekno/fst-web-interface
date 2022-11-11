<script>
    import { locale } from "../lib/locales.js";
    import {
        language_names,
    } from "../lib/langs.js";
    import { lang } from "../lib/stores.js";

    $: current_lang = language_names[$locale][$lang];
</script>

<main>
    {#if $lang}
        Du utforsker nå {current_lang}&nbsp;
        <span
            class="link"
            on:click={() => $lang = ""}
        >
            Utforsk et annet språk
        </span>
    {/if}
</main>

<style>
    main {
        display: inline-flex;
        align-items: center;
    }

    span.link {
        cursor: pointer;
        color: blue;
        text-decoration: underline;
    }
</style>
