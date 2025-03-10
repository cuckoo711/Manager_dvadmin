export interface LabelValue {
    label: string;
    value: string;
}

export interface DSLHGameBaseInfoState {
    GameName: string;
    Servers: LabelValue[];
}

export interface DSLHGameBaseInfoStates {
    data: DSLHGameBaseInfoState;
    server: string;
}