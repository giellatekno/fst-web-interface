<script>
  import { t } from "svelte-intl-precompile";
  import { locale } from "../lib/locales.js";
  import {
      lang,
      tool,
  } from "../lib/stores.js";
  import { language_names } from "../lib/langs.js";

  // Which tools are available for the
  // target language?
  function tools_for(target_lang) {
    return [
      "generate",
      "analyze",
      "disambiguate",
      "dependency",
      "hyphenation",
      "transcription",
      //"ortography",
      //"paradigm",
      //"tallordsgenerator",
      //"stedsnavnsordbok",
    ];
  }
  const x = language_names[$locale][$lang];
</script>

<p>Tilgjengelige verktøy for {x}</p>
<main>
    {#each tools_for($lang) as _tool}
        <div class="tool">
            <span
                class="title"
                on:click={() => $tool = _tool}
            >
                {$t(_tool)}
            </span>
            <br/>
            <span class="desc">
                {@html $t(_tool + ".description")}
            </span>
        </div>
    {/each}
</main>

<p>
Andre ressurser for {x}
</p>

<a href="#">Direktelenke for denne siden</a>

<style>
    div.tool { 
        margin: 12px;
    }

    div.tool > span.title {
        display: inline-block;
        text-decoration: underline;
        color: blue;
        cursor: pointer;
        font-size: 1.1em;
        margin-bottom: 6px;
    }

    div.tool > span.desc {
        font-style: italic;
        margin-left: 3em;
    }
</style>
