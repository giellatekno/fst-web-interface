<script>
    import languageIcon from "../assets/language.svg";
    import { fly } from "svelte/transition";
    import { quintOut } from "svelte/easing";
    import { locale } from "svelte-intl-precompile";
    import {
        locales,
        locales_in_locale,
    } from "../lib/locales.js";

    let open = false;
    const set_locale = loc => () => {
        $locale = loc;
        open = false;
    }
</script>

<main>
    <header>
        <img
            alt="Innholdspråk"
            on:click={() => open = !open}
            src={languageIcon}
            height="22"
        />
        <span class="lang-text">
            {locales_in_locale[$locale]}
        </span>
    </header>

    {#if open}
        <div
            in:fly={{ y: -18, duration: 170, easing: quintOut, opacity: 0.2 }}
            out:fly={{ y: -18, duration: 120, easing: quintOut, opacity: 0 }}
            class="fullscreen">
            <h1>Velg grensesnittspråk...</h1>

            {#each locales as loc}
                <div class="lang"
                     on:click={set_locale(loc)}
                     >{locales_in_locale[loc]}</div>
            {/each}
        </div>
    {/if}
</main>

<style>
    main {
        display: inline;
    }
    header {
        display: inline-flex;
        align-items: center;
    }
    header > span {
        margin-left: 0.4em;
    }
    div.fullscreen {
        padding: 26px;
        position: absolute;
        background-color: rgba(240, 245, 240, 0.95);
        left: 0; top: 28px;
        height: calc(40% - 28px);
        width: 100%;
    }
    div.lang {
        cursor: pointer;
        margin: 18px;
        font-size: 1.4em;
    }
</style>
