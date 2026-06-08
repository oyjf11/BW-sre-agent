<template>
  <div class='no-permission'>
    <el-row type='flex' class='box'>
      <el-col :span='12'>
        <img src="@/assets/error_image/none.png"></el-col>
      <el-col :span='12' class='content-wrap'>
        <p>抱歉！你暂无权限</p>
        <p>请联系管理员</p>
      </el-col>
    </el-row>
  </div>
</template>

<script>
export default {};
</script>

<style scoped lang='stylus' rel='stylesheet/stylus'>
.no-permission
  .box
    margin-top:100px;
    padding:0 10%;
    justify-content space-around
    p
      font-size:20px;
      margin-bottom 10px;
      color:#444;
    .content-wrap
      display flex;
      flex-direction column;
      justify-content center;
</style>
