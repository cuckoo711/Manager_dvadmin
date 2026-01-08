import { nextTick } from 'vue';
import '/@/theme/loading.scss';
import { showUpgrade } from "/@/utils/upgrade";


/**
 * 页面全局 Loading
 * @method start 创建 loading
 * @method done 移除 loading
 */
export const NextLoading = {
    start: () => {
        showUpgrade();
    },
    done: (time: number = 5000) => {
        nextTick(() => {
            setTimeout(() => {
                window.nextLoading = false;
                const el = document.querySelector('.loading-next');
                el?.parentNode?.removeChild(el);
                console.log('Loading removed');
            }, time);
        }).then();
    },
};