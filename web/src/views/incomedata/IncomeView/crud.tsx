import * as api from './api'

export const getIncome = async (obj: any = null) => {
    return await api.getIncome(obj);
}

export const exportIncome = async (date: string, type: string) => {
    return await api.exportIncome(date, type);
}

export const GetIncomeExport = async (obj: any) => {
    return await api.GetIncomeExport(obj);
}
