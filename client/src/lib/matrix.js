import { pad_center } from "./utils.js";

const __Empty = Symbol("__Empty");
export class Entry {
    #value;
    #empty_indicator;

    constructor(value, empty_indicator = "-") {
        if (value) {
            this.#value = value;
        } else {
            this.#value = __Empty;
        }

        this.#empty_indicator = empty_indicator;
    }

    [Symbol.toPrimitive]() {
        if (this.#value === __Empty) {
            return this.#empty_indicator;
        }
        return String(this.#value);
    }

    is_empty() { return this.#value === __Empty; }
    clear() { this.#value = __Empty; }
    set(value) { this.#value = value; }

    get value() { return this[Symbol.toPrimitive](); }
    valueOf() { return this.value; }
    toString() { return this.value; }
    toJSON() { return "Entry { value: " + String(this.#value) + " }" }
}

export class Matrix {
    #data;
    #x;
    #y;

    constructor(y, x, fill=undefined, data=null) {
        this.#x = x;
        this.#y = y;
        if (data) {
            this.#data = data;
        } else {
            this.#data = Array(y).fill(null).map(_ => Array(x).fill(fill));
        }
    }

    get rows() { return this.#data; }
    get width() { return this.#x; }
    get height() { return this.#y; }

    [Symbol.toPrimitive]() {
        return `${this.constructor.name}<${this.#y}, ${this.#x}>`;
    }
    str() { return this[Symbol.toPrimitive](); }

    as_console_str({ empty_indicator = "-" } = {}) {
        const lines = [];

        let longest_column = -1;
        for (let y = 0; y < this.#y; y++) {
            const cols = [];

            for (let x = 0; x < this.#x; x++) {
                let val = String(this.#data[y][x]);
                if (val === "undefined" || val === "null") {
                    val = empty_indicator;
                }

                longest_column = Math.max(longest_column, val.length);

                cols.push(val);
            }

            lines.push(cols);
        }

        for (let line of lines) {
            let this_column_length = line
                .map(col => col.length)
                .reduce((prev, cur) => Math.max(prev, cur));
            longest_column = Math.max(this_column_length, longest_column);
        }

        const new_lines = [];
        for (let line of lines) {
            const new_col = [];
            for (let col of line) {
                const new_entry = pad_center(col, longest_column);
                new_col.push(new_entry);
            }
            new_lines.push(new_col.join(" | "));
        }

        return new_lines.join("\n");
    }

    #boundcheck(y, x, funcname) {
        let errors = [];
        if (y >= this.#y) {
            errors.push(`y=${y} is too large (max y coord is ${this.#y - 1})`);
        } else if (y < 0) {
            errors.push(`y=${y} is too small (min y coord is 0)`);
        }
        if (x >= this.#x) {
            errors.push(`x=${x} is too large (max x coord is ${this.#x - 1})`);
        } else if (x < 0) {
            errors.push(`x=${x} is too small (min x coord is 0)`);
        }
        if (errors.length > 0) {
            throw new Error(`${funcname}(y, x): out of bounds: ` + errors.join(", "));
        }
    }

    get(y, x) {
        this.#boundcheck(y, x, "get");
        return this.#data[y][x];
    }

    set(y, x, value) {
        this.#boundcheck(y, x, "set");
        this.#data[y][x] = value;
    }

    without_empty_columns_and_rows() {
        const keep_rows = Array(this.#y).fill(false);
        const keep_cols = Array(this.#x).fill(false);

        const kept_cols = {};
        const kept_rows = {};

        for (let y = 0; y < this.#y; y++) {
            for (let x = 0; x < this.#x; x++) {
                if (typeof this.#data[y][x] !== "undefined") {
                    keep_rows[y] = true;
                    keep_cols[x] = true;
                }
            }
        }

        const n_y = keep_rows.filter(x => !!x).length;
        const n_x = keep_cols.filter(x => !!x).length;
        let n = new Matrix(n_y, n_x);

        let yy = 0;
        for (let y = 0; y < this.#y; y++) {
            if (!keep_rows[y]) {
                continue;
            }
            let xx = 0;

            for (let x = 0; x < this.#x; x++) {
                if (!keep_cols[x]) {
                    continue;
                }
                n.set(yy, xx, this.get(y, x));
                kept_cols[x] = xx;
                kept_rows[y] = yy;
                xx++;
            }

            yy++;
        }

        return {
            matrix: n,
            kept_cols,
            kept_rows,
        };
    }

    transpose() {
        let n = new Matrix(this.#x, this.#y);
        for (let y = 0; y < this.#y; y++) {
            for (let x = 0; x < this.#x; x++) {
                n.set(x, y, this.#data[y][x]);
            }
        }
        return n;
    }
}

