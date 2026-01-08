declare module 'Nzh' {
    export const cn: {
        toMoney: (value: number) => string;
        encodeS: (value: string) => string;
        decodeS: (value: string) => string;
    };

    export const hk: {
        toMoney: (value: number) => string;
        encodeS: (value: string) => string;
        decodeS: (value: string) => string;
    };
}
