import {request} from '/@/utils/service';



export async function GetDomainIps(domains: string,) {
    return request({
        url: '/api/tools/get_domain_ips/',
        method: 'post',
        data: {
            domains: domains
        }
    })
}