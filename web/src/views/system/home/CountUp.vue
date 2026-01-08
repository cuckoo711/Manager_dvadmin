<template>
  <span>{{ displayNumber }}</span>
</template>

<script lang="ts">
import { defineComponent, ref, watch } from 'vue';

export default defineComponent({
  name: 'CountUp',
  props: {
    target: {
      type: Number,
      required: true,
    },
    duration: {
      type: Number,
      default: 800, // 动画持续时间，单位毫秒
    },
    decimalPlaces: {
      type: Number,
      default: 0, // 小数位数
    },
  },
  setup(props) {
    const displayNumber = ref(0);

    const animate = () => {
      const start = performance.now();
      const duration = props.duration;
      const target = props.target;
      const decimalMultiplier = Math.pow(10, props.decimalPlaces);

      const step = (currentTime: number) => {
        const elapsed = currentTime - start;
        if (elapsed < duration) {
          const progress = elapsed / duration;
          displayNumber.value = Math.floor(progress * target * decimalMultiplier) / decimalMultiplier;
          requestAnimationFrame(step);
        } else {
          displayNumber.value = target;
        }
      };

      requestAnimationFrame(step);
    };

    watch(
      () => props.target,
      () => {
        animate();
      },
      { immediate: true }
    );

    return {
      displayNumber,
    };
  },
});
</script>

<style scoped>
/* 可根据需要添加样式 */
</style>
