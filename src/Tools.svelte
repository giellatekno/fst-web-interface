<script>
  import { t } from "svelte-intl-precompile";
  import {
      target_lang,
      selected_tool,
  } from "./lib/stores.js";

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
</script>

<p>Tilgjengelige verktøy for {$target_lang}</p>
<main>
    {#each tools_for($target_lang) as tool}
        <div class="tool">
            <span
                class="title"
                on:click={() => $selected_tool = tool}
            >
                {$t(tool)}
            </span>
            <br/>
            <span class="desc">
                {@html $t(tool + ".description")}
            </span>
        </div>
    {/each}
</main>

<p>
Andre ressurser for {$target_lang}
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
