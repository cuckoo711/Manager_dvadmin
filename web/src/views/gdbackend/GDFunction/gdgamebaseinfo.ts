export interface LabelValue {
    label: string;
    value: string;
}

export interface GDGameBaseInfoState {
    GameName: string;
    WebUrl: string;
    Servers: LabelValue[];
    ServerTime: {};
    Actions: LabelValue[];
    Reasons: LabelValue[];
    Activetype: LabelValue[];
    CombinedServices: LabelValue[];
    Gifts: LabelValue[];
    Sids: LabelValue[];
    SidsDict: {
        menkes: LabelValue[];
        props: LabelValue[];
        wifes: LabelValue[];
    };
}

export interface GDGameBaseInfoStates {
    data: GDGameBaseInfoState;
    token: string;
}