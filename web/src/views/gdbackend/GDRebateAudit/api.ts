import { request } from '/@/utils/service';

export const apiPrefix = '/api/GDRebateAudit/';

export function GetList(query: any) {
  return request({
    url: apiPrefix,
    method: 'get',
    params: query,
  });
}

export function AddObj(obj: any) {
  return request({
    url: apiPrefix,
    method: 'post',
    data: obj,
  });
}

export function UpdateObj(obj: any) {
  return request({
    url: apiPrefix + obj.id + '/',
    method: 'put',
    data: obj,
  });
}

export function DelObj(id: number) {
  return request({
    url: apiPrefix + id + '/',
    method: 'delete',
  });
}

export function Approve(id: number) {
  return request({
    url: `${apiPrefix}${id}/approve/`,
    method: 'post',
  });
}

export function Cancel(id: number) {
  return request({
    url: `${apiPrefix}${id}/cancel/`,
    method: 'post',
  });
}

export function Issue(id: number) {
  return request({
    url: `${apiPrefix}${id}/issue/`,
    method: 'post',
  });
}

export function BatchApprove(ids: Array<number>) {
  return request({
    url: `${apiPrefix}batch_approve/`,
    method: 'post',
    data: { ids },
  });
}

export function BatchCancel(ids: Array<number>) {
  return request({
    url: `${apiPrefix}batch_cancel/`,
    method: 'post',
    data: { ids },
  });
}

export function BatchIssue(ids: Array<number>) {
  return request({
    url: `${apiPrefix}batch_issue/`,
    method: 'post',
    data: { ids },
  });
}
