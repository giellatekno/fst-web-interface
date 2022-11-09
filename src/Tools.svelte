<script>
  import {
    addMessages,
    init,
    getLocaleFromNavigator,
    /* register, */
  } from 'svelte-intl-precompile';

  import nob from "../locales/nob.json";
  import eng from "../locales/eng.json";
  import { t } from "svelte-intl-precompile";
  addMessages('nob', nob);
  addMessages('eng', eng);

  init({
    fallbackLocale: 'nob',
    initialLocale: 'nob', /*getLocaleFromNavigator()*/
  });
  export let lang;

  function tools_for(lang) {
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

<p>Tilgjengelige verktøy for {lang}</p>
<div>
{#each tools_for(lang) as tool}
  <div class="tool">
    <span class="title">{$t(tool)}</span><br/>
    <span class="desc">{@html $t(tool + ".description")}</span>
  </div>
{/each}
............
</div>

<p>
Andre ressurser for {lang}
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
