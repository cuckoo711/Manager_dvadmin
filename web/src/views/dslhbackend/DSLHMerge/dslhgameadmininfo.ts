export type ServerState = "新服" | "火爆" | "维护" | "屏蔽";
export type BoolState = "是" | "否";

export interface ServerConfig {
    server_name: string;       // 服务器名称
    server_id: string;         // 服务器ID
    server_ip: string;         // 服务器IP
    open_time: string;         // 开服时间
    database_user: string;     // 数据库用户名
    database_name: string;     // 数据库名称
    database_port: string;     // 数据库端口
    server_is_open: BoolState;    // 服务器是否开启 ("是" 或 "否")
    server_url: string;        // 服务器URL
    server_port: string;       // 服务器端口
    is_merged: BoolState;         // 是否合服 ("是" 或 "否")
    server_type: ServerState;       // 服务器状态 (如"屏蔽", "新服")
}

export interface DSLHGameAdminInfoState {
    servers: string[];                 // 服务器名称列表
    has_recharges: string[];           // 有充值记录的服务器列表
    no_recharges: string[];            // 无充值记录的服务器列表
    server_config: {                   // 每个服务器的详细配置信息
        [key: string]: ServerConfig;  // 键为服务器名称，值为ServerConfig对象
    };
    gamename: string;                  // 游戏名称
    server_id: string;                 // 当前操作的服务器ID
}

export interface DSLHGameAdminInfoStates {
    data: DSLHGameAdminInfoState;      // 包含主要服务器配置信息的对象
}