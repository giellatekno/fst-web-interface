<script>
    import icon from "../assets/search.svg";
    import { t } from "svelte-intl-precompile";
    export let value;
</script>

<div>
    <img src={icon} width="20" height="20">
    <input bind:value placeholder="{$t("search")}...">
</div>

<style>
    div {
        box-sizing: border-box;
        display: inline-flex;
        align-items: center;
        padding: 6px;
        min-height: 3em;
    }
    img {
        margin-right: 8px;
    }
    input {
        font-size: 16px;
        font-family: Roboto, sans-serif;
        width: 8em;
        border-radius: 12px;
        border: 2px solid #dadada;
        padding: 8px;
        transition:
            width ease-out 0.15s,
            border-radius ease-out 0.15s,
            border-color ease-out 0.15s;
    }
    input:focus {
        width: 100%;
        border-radius: 6px;
        border: 2px solid #7777ee;
        outline: none;
    }
</style>
