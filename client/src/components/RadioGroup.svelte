<script>
    import { createEventDispatcher } from "svelte";
    const dispatch = createEventDispatcher();

    export let header;
    export let choices;
    export let selected;

    function select_choice(choice) {
        dispatch("new-select", choice);
        selected = choice;
    }

    function enter_and_space(fn) {
        return function (ev) {
            if (ev.key === "Enter" || ev.key === " ") fn();
        }
    }
</script>

<div>
    <header>{header}</header>

    {#each choices as choice}
        <span
            role="button"
            tabindex="0"
            class:on={selected === choice}
            on:click={() => select_choice(choice)}
            on:keydown={enter_and_space(() => select_choice(choice))}
        >
            <label>{choice}</label>
            <input
                type="radio"
                bind:group={selected}
                name="group"
                value={choice}
            >
        </span>
    {/each}
</div>

<style>
    div {
        display: flex;
        font-variant: small-caps;
        user-select: none;
        margin: 8px 0;
    }

    div > header {
        font-size: 18px;
        font-weight: bold;
        padding: 2px 8px;
        border-radius: 5px;
        color: #000;
    }

    div > span {
        font-size: 16px;
        margin-left: 16px;
        padding: 4px 12px;
        border-radius: 5px;
        background-color: #d9d9d9;
        color: #292929;
        font-weight: bold;
        transition:
            background-color 0.2s ease-out,
            color 0.2s ease-out;
    }

    div > span.on {
        background-color: #4651ea;
        color: white;
    }

    div > span:hover,
    div > span > label:hover {
        cursor: pointer;
    }

    div > span.on:focus-within {
        outline: 2px solid orange;
    }

    div input {
        appearance: none;
        display: none;
    }

    @media screen and (max-width: 880px) {
        div {
            flex-wrap: wrap;
        }

        div > header {
            width: 100%;
        }

        div > span {
            margin-left: 0;
            margin-right: 16px;
        }
    }

    @media screen and (max-width: 750px) {
        div > header {
            margin-bottom: 0;
        }
        div > span {
            margin-top: 8px;
        }
    }
</style>
