<template>
  <div class="orderConfirm">
    <div class="messageConfirmBox">
      <div class="stepsContainer" v-if="payStep!=3">
        <el-steps :active="payStep" align-center>
          <el-step title="确认订单"></el-step>
          <el-step title="支付订单"></el-step>
          <el-step title="完成购买"></el-step>
        </el-steps>
      </div>
      <div class="stepOne" v-if="payStep==1">
        <div class="orgData">开通机构：{{serviceList[0].org_name}}</div>
        <div class="serviceTable">
          <el-table
            class="pub-table"
            v-loading="tableLoading"
            slot="table"
            ref="tableList"
            :data="serviceList"
            style="width: 100%"
          >
            <el-table-column prop="service_name" label="应用" width="440" fixed="left"></el-table-column>
            <el-table-column prop="sku_name" label="套餐" width="140" fixed="left"></el-table-column>
            <el-table-column prop="sku_num" label="数量" width="140" fixed="left"></el-table-column>
            <el-table-column label="开始时间" prop="start_time" width="140"></el-table-column>
            <el-table-column prop="end_time" label="结束时间" width="140"></el-table-column>
            <el-table-column prop="order_money" label="总价 = 数量*单价" width="140"></el-table-column>
          </el-table>
        </div>
        <div class="addressBox" v-if="serviceList[0].is_feed==1">
          <div class="appDetailBar">
            <span class="detailLeft"></span>
            <div class="detailRight">你选购的内容包含了物件邮寄，需要留下您的联系方式和邮寄地址</div>
          </div>
          <!-- <div class="addressTips">你选购的内容包含了物件邮寄，需要留下您的联系方式和邮寄地址</div> -->
          <div class="appDetailBar">
            <span class="detailLeft">联系人</span>
            <div class="detailRight">
              <el-input v-model="orderData.name" placeholder="请输入联系人姓名"></el-input>
            </div>
          </div>
          <div class="appDetailBar">
            <span class="detailLeft">联系电话</span>
            <div class="detailRight">
              <el-input v-model="orderData.phone" placeholder="请输入联系人电话"></el-input>
            </div>
          </div>
          <div class="appDetailBar">
            <span class="detailLeft">邮寄地址</span>
            <div class="detailRight">
              <el-cascader
                placeholder="选择地址"
                v-model="orderData.city"
                :options="cityOptions"
                filterable
                @change="cityChoose"
                :props="{value:'label'}"
              ></el-cascader>
              <!-- <el-input v-model="input" placeholder=""></el-input> -->
            </div>
          </div>
          <div class="appDetailBar">
            <span class="detailLeft"></span>
            <div class="detailRight detailRightLong">
              <el-input v-model="orderData.addressDetail" placeholder="详细地址"></el-input>
            </div>
          </div>
        </div>
      </div>
      <div class="payBox" v-if="payStep==1">
        <div style="line-height:20px;margin-bottom: 20px">支付方式</div>
        <div class="payTypeBar">
          <div
            class="payTypeBoxWrap"
            v-for="(pay,payIdx) in payTypeList"
            :key="payIdx"
            @click="orderData.payment_type=pay.value"
          >
            <div :class="['payTypeBox',orderData.payment_type==pay.value?'payTypeChosen':'']">
              {{pay.label}}
              <i class="el-icon-check" v-show="orderData.payment_type==pay.value"></i>
            </div>
          </div>
        </div>
        <div class="agreementBar">
          <input type="checkbox" class="agreementCheck" v-model="agreementIfCheck" />同意
          <el-button type="text" @click="showAgreement()">《章鱼校长用户购买协议》</el-button>
        </div>
        <div class="actBar">
          共计
          <span class="redFont">￥{{orderData.order_money}}</span>
          <el-button type="primary" @click="postOrder">提交订单</el-button>
        </div>
      </div>
      <div class="stepTwo" v-if="payStep==2">
        <div class="scanBox">
          <div class="scanBar">
            应用名称：
            <span style="color:#3a3d57">{{steptwoData.service_name}}</span>
          </div>
          <div class="scanBar">
            开通机构：
            <span style="color:#3a3d57">{{steptwoData.org_name}}</span>
          </div>
          <div class="scanBar">
            应用套餐：
            <span style="color:#3a3d57">{{steptwoData.sku_name}}</span>
          </div>
          <div class="scanBar">
            购买数量：
            <span style="color:#3a3d57">{{steptwoData.sku_num}}</span>
          </div>
          <div class="scanBar">
            使用期限至：
            <span style="color:#3a3d57">{{steptwoData.end_time=='-'?'-':$formatToDate(steptwoData.end_time,'Y-M-D')}}</span>
          </div>
          <div class="scanBar">
            付款金额：
            <span style="color:#3a3d57">{{steptwoData.sku_money}}</span>
          </div>
          <div class="qrcodeBox">
            <qrcode :value="steptwoData.code_url" :options="{ size: 260 }"></qrcode>
            <!-- <img :src="steptwoData.pay_url" alt class="scanImg" /> -->
          </div>
          <div class="payHelpBar">
            <!-- <el-button type="text" class="payHelpFont">支付遇到问题</el-button>
            <div class="midBorder"></div> -->
            <el-button type="text" class="payHelpFont" @click="checkPayStatus(true)">我已完成支付</el-button>
          </div>
        </div>
      </div>
      <div class="stepThree" v-if="payStep==3">
        <i class="el-icon-circle-check"></i>
        <div class="bigFont">恭喜你，开通成功</div>
        <div class="successTips">
          <div class="tipsTitle">您还可以进行以下操作</div>
          <div class="tipsBar">
            1、开通成功后，可以直接跳转到功能
            <el-button type="text" @click="goTo('appStoreMyApp')">立即使用></el-button>
          </div>
          <div class="tipsBar">
            1、开通成功后，可以在组织架构-角色管理将应用的使用权限分配给其他用户
            <el-button type="text" @click="goTo('organization_control')">立即分配></el-button>
          </div>
        </div>
        <div class="btnBar">
          <el-button type="primary" @click="goTo('appStoreMyApp')">查看已开通应用</el-button>
          <el-button type="info" @click="goTo('appStoreList')">返回应用商城</el-button>
        </div>
      </div>
      <div class="agreementContainer" v-if="agreementShow">
        <div class="agreementTitle">章鱼校长用户购买协议</div>
        <div class="agreementContentContainer">
          <div class="agreementShortContent">
            <div class="shortTitle">一.导语</div>
            <div class="agreementDetail">
              (一)
              【审慎阅读】你在购买应用的流程中点击同意本协议之前，应当认真阅读本协议。请你务必审慎阅读、充分理解各条款内容，特别是免除或者限制责任的条款、法律适用和争议解决条款。免除或者限制责任的条款将以粗体下划线标识，你应重点阅读。
              <br />(二)
              【签约流程】当你阅读并同意本协议且完成订购程序后，即表示你已充分阅读、理解并接受本协议的全部内容。阅读本协议的过程中，如果你不同意本协议或其中任何条款约定，你应立即停止订购应用商城的任何一款应用。
            </div>
          </div>
          <div class="agreementShortContent">
            <div class="shortTitle">二.协议的生效与变更</div>
            <div class="agreementDetail">
              (一)【协议变更】小云翰可基于国家法律法规变化、业务调整、产品更新及维护交易秩序、保护你权益等需要对协议内容进行变更，变更后的协议将按照法定程序进行公示并在小云翰官网的新闻中心板块公告。
              <br />(二)
              【协议生效】若你在本协议内容公告变更后继续使用本服务的，表示你已充分阅读、理解并接受变更后的协议内容，也将遵循变更后的协议内容继续使用小云翰的应用服务；若你不同意变更后的协议内容，你应停止使用本服务。小云翰及你的一切行为、争议应依据具体行为、争议发生时最新生效版本的《小云翰应用商城使用协议》作出并进行解释。
              <br />(三)
              【民事权利能力和民事行为能力】你确认，你是具有法律规定的完全民事权利能力和民事行为能力，能够独立承担民事责任的自然人、法人或其他组织；本协议内容不受你所属国家或地区的排斥。若你不具备前述与你行为相适应的民事行为能力，则你及你的监护人应依照法律规定承担因此而导致的后果。
              <br />(四)
              【补充协议】你与小云翰签署的本协议列明的条款并不能完整罗列并覆盖你与小云翰所有权利与义务，现有的约定也不能保证完全符合未来发展的需求。因此，与小云翰及你相关的规则均为本协议的补充协议，与本协议不可分割且具有同等法律效力。如你使用小云翰提供的服务，视为你同意上述补充协议。
            </div>
          </div>
          <div class="agreementShortContent">
            <div class="shortTitle">三.定义</div>
            <div class="agreementDetail">
              <br />(一)
              小云翰：是指研发并提供小云翰产品和服务的深圳市云翰教育科技有限公司、深圳认知计算有限公司，及现在或未来设立的相关关联公司的单称或合称。
              <br />(二)
              服务商：指有效申请并经小云翰审核同意后，在小云翰应用商城发布应用程序作品的发布者。
              <br />(三)
              小云翰开放平台：指基于小云翰平台各类电子商务业务的开放，由小云翰提供一些软件和支持材料，服务商通过这些软件和支持材料开发应用以便服务于自身或服务于小云翰平台其他用户。服务商可以通过小云翰开放平台的能力开发指定的功能服务。
              <br />(四)
              小云翰应用商城：是指小云翰负责运营的应用发布平台。
              <br />(五)
              应用：指小云翰自行开发或服务商基于小云翰开放平台所开发的软件或服务。
              <br />(六)
              用户（以下或称“你”）：指所有直接或间接使用服务商发布或更新至小云翰应用商城上的作品的使用者。
            </div>
          </div>
          <div class="agreementShortContent">
            <div class="shortTitle">四.小云翰对你的行为的免责</div>
            <div class="agreementDetail">
              你在通过小云翰应用商城（以下可简称“应用商城”）订购使用任何服务商基于小云翰开放平台开发的应用之前，请仔细阅读下述免责条款。小云翰对于你的以下行为不承担任何责任：
              <br />(一)
              你使用服务商应用的某一行为或多种行为不符合国家法律法规的规定，或通过应用从事非法活动，或侵害服务商和任何第三方的合法权益，包括但不限于以下内容而造成的相关责任由你自行承担：
              <br />1.通过服务商提供的应用上传、下载、储存、传播、邮件发送或者提供任何具有非法性、威胁性、危害性、诽谤性、侮辱性、暴力、淫秽、种族或民族歧视，或其他冒犯性的内容；
              <br />2.出售、转售或复制、开发服务商授予的使用权限；
              <br />3.复制和模仿服务商的设计理念、界面、功能和图表；
              <br />4.未经服务商许可基于服务商的应用或其内容进行修改或制造派生其他产品；
              <br />5.你或你的员工、代理、咨询者或顾问对服务商应用和/或服务商应用任何部分（软件产品、页面标识、服务品牌、资讯、信息）进行复制、翻译、修改、适应、增强、反编译、反汇编、反向工程、分解拆卸、出售、转租或作任何商业目的的使用；
              <br />6.其他违反国家法律、法规、政策或者本协议的行为。
              <br />(二)
              你未按时足额向服务商支付软件许可费用，导致服务商终止与你的合作，由此引发的一系列损失（包括数据信息的丢失、财产损失等）由你自行承担。
              <br />(三)
              你未严格按照应用的使用说明和/或操作说明使用应用所引发的一切法律后果由你自行承担；如因你使用服务商应用的行为，导致服务商或任何第三方为此承担了相关责任的，则你需全额赔偿服务商或任何第三方的相关支出及损失，包括但不限于合理的律师费等。
              <br />(四)
              交易是你与服务商自行达成的，你在订购服务商提供的应用之前，应自行与服务商签署相应的《软件许可协议》，并严格按照协议的约定履行。如因交易发生任何争议，可以请小云翰介入协调，但不应就交易纠纷追究小云翰的任何责任。
            </div>
          </div>
          <div class="agreementShortContent">
            <div class="shortTitle">五.小云翰对其他情况的免责</div>
            <div class="agreementDetail">
              你在通过小云翰应用商城（以下可简称“应用商城”）订购使用任何服务商基于小云翰开放平台开发的应用之前，请仔细阅读下述免责条款。小云翰在以下情况下不承担任何责任：
              (一)
              小云翰因现有技术限制导致应用可能存在瑕疵而使你在使用服务商应用所致的损害免责。
              <br />(二)
              如因非小云翰原因造成的网络问题导致服务商应用无法按指定的时间正常使用所致的损害免责。
              <br />(三)
              小云翰仅作为小云翰应用商城的提供者，而并非单个应用的服务商，小云翰无须就服务商提供的应用向你承担任何责任。因服务商的应用或服务商的行为，致使你的保密信息泄露或财产遭受损失的，服务商为唯一责任人，你无权向小云翰主张损害赔偿责任。
              <br />(四)
              你理解并同意，如服务商违反了其与小云翰的合作协议，则小云翰有权随时终止与服务商的合作。此等情况下，你可能无法继续使用该服务商的应用。该等情况的发生属于服务商过错或过失，相关责任应由服务商独立承担，小云翰不因此承担任何责任，但小云翰将尽力督促服务商弥补你的损失。
              <br />(五)
              小云翰为应用制定了严格的检测项目，但任何检测项目均不能保证应用完全可靠。小云翰对应用可能存在的缺陷或错误不提供任何保证或担保，对你使用应用可能产生的损失也不承担违约或任何其他责任。
              <br />(六)
              小云翰应用商城仅作为服务商和你物色交易对象的地点，因此，小云翰不对服务商和你行为的合法性、有效性及应用的真实性、合法性和有效性作任何明示或默示的保证。小云翰在你与服务商产生纠纷时将努力进行协调，服务商也应秉承为你提供优质服务的理念为你提供便利，但小云翰并不保证协调取得实际效果。
              <br />(七)
              对于服务商提供的应用，由于网上交易平台的特殊性，小云翰对应用的审核不可能完备且小云翰并不控制该等应用，你承认并同意，小云翰并不对该等应用的可用性负责，并不对应用所涉及的任何内容、宣传资料或其他材料作任何明示或默示的认可，也不对其等负责或承担任何责任。你进一步承认和同意，对于任何因使用应用而获取的内容、宣传资料或其他材料而造成（或声称造成）的任何直接或间接损失，小云翰均不承担责任。
              <br />(八)
              如果由于黑客攻击或政府管制或网络通讯瘫痪等对其发生和后果不能预见的事件，服务商和你均确认此属不可抗力；在不可抗力下，你同意小云翰、服务商及第三方无须对本协议的延期履行、不能履行承担任何责任。
            </div>
          </div>
          <div class="agreementShortContent">
            <div class="shortTitle">六.权利义务条款</div>
            <div class="agreementDetail">
              (一)
              用户需保证其使用服务商提供的应用时的各项行为符合国家法律法规的规定，合法真实且不侵害任何第三方的合法权益。
              <br />(二)
              用户应按时足额支付因使用服务商所提供的应用而产生的服务费（如有），否则服务商可能将终止用户使用的权利，用户应对服务商终止提供服务而可能造成的损害自行承担全部责任。
              <br />(三)
              用户知悉，服务商提供的应用受到《版权法》等相关的知识产权法律、法规和条约的保护。服务商授权用户许可使用，而非出售。
              <br />(四)
              用户知悉，若用户购买的为“设计类”应用，小云翰将为用户在后台静默地初始化资源管理平台，但资源管理平台可管理的文件类型，可管理空间、文件数等均由小云翰决定，且小云翰保留向用户收费的权利。
            </div>
          </div>
          <div class="agreementShortContent">
            <div class="shortTitle">七.支付条款</div>
            <div class="agreementDetail">
              <br />(一)
              本条所提及的“小云翰支付”是指由财付通支付科技有限公司（以下简称：微信支付）提供的货币资金转移及账户号管理服务。
              <br />(二)
              你向服务商支付应用或应用内服务的费用时，所产生的资金处理服务均通过“小云翰支付”完成。在支付前，你需自行完成“小云翰支付”账户的开户动作并签署相关协议，否则，有可能无法完成支付。
              <br />(三)
              本协议中所述的应用由服务商提供，您也许需要接受服务商的协议和收费才能下载和使用他们的应用。你知悉，服务商可以保留调整应用价格的权利并在你购买相应的应用之前适时告知你。
              <br />(四)
              你所订购的应用的费用以你下单页面显示为准。由于费用将由你直接支付给服务商，因此若你在支付费用后如需开具发票的，你应自行向服务商提出申请并由服务商负责开具。因交易而产生的税费也应由你和服务商自行承担。
              <br />(五)
              由于考虑到服务商提供的收费服务存在不确定性，所以小云翰不支持也不鼓励服务商为你提供不设时限或次数等条件的收费服务。你在购买服务商提供的不设时限或次数等条件的收费服务时应尤其注意应用可能停止提供或终止提供的风险。若因你未注意导致付费后停止提供或终止提供，且服务商不退还费用的，小云翰不承担任何责任。
              <br />(六)
              小云翰不赞成服务商在你使用应用过程中另行增加收费项目，但服务商有可能不遵守其与小云翰的约定，在你支付费用后另行加收费用，你在使用应用时通过应用界面的链接、收费按钮或渠道支付费用时，应尤其注意费用损失的风险。
              <br />(七)
              你要求退款的，服务商可能根据收费标准或退款规定等原因拒绝退款，届时你无权直接要求小云翰进行退款。但小云翰会根据你的投诉反馈对服务商提供的收费服务进行评估，如依照小云翰的判断服务商提供的收费服务存在过错或过失的，小云翰可协调服务商向你退款。你应理解小云翰的协调努力可能没有实际效果，届时你不应要求小云翰进行赔偿或补偿。
            </div>
          </div>
          <div class="agreementShortContent">
            <div class="shortTitle">八.服务的使用期限与协议的终止</div>
            <div class="agreementDetail">
              (一)
              用户所购买应用的使用期限以下单页面显示为准。
              <br />(二)
              出现下列情况之一的，服务商有权或小云翰有权要求服务商终止继续提供应用服务，而无需承担任何责任：
              <br />1.用户购买的应用已到期且未续费的。
              <br />2.用户严重违反本协议项下条款的约定的。
            </div>
          </div>
          <div class="agreementShortContent">
            <div class="shortTitle">九.通知与送达</div>
            <div class="agreementDetail">
              (一)
              【联系方式有效】用户在注册小云翰账户时，应该向小云翰提供真实有效的联系方式（包括但不限于电子邮件地址、联系电话、联系地址等），对于联系方式发生变更的，服务商有义务及时更新有关信息，并保持可被联系的状态。
              <br />(二)
              【通知的送达】本协议签订或履行过程中，小云翰寄送的书面通知，在交邮后第五个自然日即视为送达。书面通知形式还包括但不限于在小云翰平台公告、电子邮件、平台站内信、系统信息、手机短信、QQ消息和传真等电子方式，在采用电子方式进行通知的情况下，发送当日即视为送达。
              <br />(三)
              【法律文书送达】对于在小云翰开放平台平台上因交易活动引起的任何纠纷，用户同意司法机关（包括但不限于人民法院）可以通过用户在平台注册、更新时提供的手机号码、电子邮箱联系方式以及在注册成为小云翰开放平台用户时生成的账号进行送达，司法机关向上述联系方式发出法律文书即视为送达。用户指定的邮寄地址为法定联系地址或提供的有效联系地址。
              <br />(四)
              【联系方式实时更新】用户应当保证所提供的联系方式是准确、有效的，并进行实时更新。如果因提供的联系方式不正确，或不及时告知变更后的联系方式，使法律文书无法送达或未及时送达，由用户自行承担由此可能产生的法律后果。
            </div>
          </div>
          <div class="agreementShortContent">
            <div class="shortTitle">十.法律的适用、管辖与其他</div>
            <div class="agreementDetail">
              <br />(一)
              【法律适用】本协议之效力、解释、变更、执行与争议解决均适用中华人民共和国法律，没有相关法律规定的，参照通用国际商业惯例和（或）行业惯例。
              <br />(二)
              【管辖法院】因本协议所产生的争议，由小云翰与服务商、用户共同协商解决。协商不成时，任何一方均可向浙江省杭州市西湖区人民法院提起诉讼。
              <br />(三)
              【条款独立性】如本协议的任何条款被视作无效或无法执行，则上述条款可被分离，其余条款则仍具有法律效力。
              <br />(四)
              【权利放弃】本协议任何一方于另一方过失或违约时放弃本协议规定的权利的，不得视为其对一方的其他或以后同类之过失或违约行为弃权。小云翰未行使或执行本协议任何权利或规定，不构成对前述权利或权利之放弃。
            </div>
          </div>
        </div>
        <div class="btnBar">
          <el-button
            type="primary"
            :disabled="agreementCount>0"
            @click="agreementShow=false;agreementIfCheck=true"
          >
            同意
            <span v-show="agreementCount">{{`(${agreementCount})`}}</span>
          </el-button>
          <el-button type="info" plain @click="agreementShow=false">取消</el-button>
        </div>
      </div>
      <div class="toBlack" v-show="agreementShow"></div>
    </div>
  </div>
</template>

<script>
import addressJson from "@/assets/address_json/city.json";
import {
  createOrder,
  getPayCode,
  getPayStatus,
  getOrderDetail
} from "@/api/app_store.js";
import VueQrcode from "@xkeshi/vue-qrcode";
import { setInterval } from "timers";
var payStatusInterval = [];
var agreementInterval = [];
export default {
  props: {},
  data() {
    return {
      tableLoading: false,
      agreementIfCheck: false,
      payStep: 0,
      orderId: 0,
      agreementShow: false,
      agreementCount: 3,
      serviceList: [{ is_feed: 0 }],
      payTypeList: [
        { value: "scan", label: "扫码支付" }
        // { value: "hip", label: "屁股支付" }
      ],
      cityOptions: [],
      orderData: {
        name: "",
        phone: "",
        city: "",
        addressDetail: "",
        payment_type: "scan",
        order_money: 0
      },
      steptwoData: {},
      agreementData: {
        ifShow: false,
        count: 0,
        dataList: [{ title: "1.总则" }]
      }
    };
  },
  components: {
    qrcode: VueQrcode
  },
  methods: {
    goTo(name) {
      this.$router.push({
        name: name,
        params:{active:1}
      });
    },
    postOrder(e) {
      let postData = {
        service_id: this.serviceList[0].service_id,
        sku_id: this.serviceList[0].sku_id,
        org_buy_id: this.serviceList[0].org_buy_id,
        sku_num: this.serviceList[0].sku_num,
        payment_type: this.orderData.payment_type
      };
      if (!this.agreementIfCheck) {
        this.$message({
          message: "请阅读购买协议后勾选",
          type: "warning"
        });
        return;
      }
      //1为物料，需要收货信息
      if (this.serviceList[0].is_feed == 1) {
        let orderData = this.orderData;
        if (
          orderData.name &&
          orderData.phone &&
          orderData.city &&
          orderData.addressDetail
        ) {
          Object.assign(postData, {
            province: this.orderData.city[0],
            city: this.orderData.city[1],
            district: this.orderData.city[2],
            address: this.orderData.addressDetail,
            phone: this.orderData.phone,
            consignee: this.orderData.name
          });
        } else {
          this.$message({
            message:
              "您选购的内容包含了物件邮寄，需要留下您的联系方式和邮寄地址",
            type: "warning"
          });
          return;
        }
      }
      createOrder(postData).then(data => {
        this.orderId = data.data;
        this.getOrderData(data.data);
        this.takePayCode(data.data);
      }).catch(err=>{
          this.$message({
              message:err,
              type:'warning'
          })
      })
      console.log(postData);
    },
    takePayCode(order_id) {
      getPayCode({ order_id }).then(data => {
          if (data.data.err_code_des) {
              this.$message({
                  message:data.data.err_code_des,
                  type:'warning'
              })
          }
        this.steptwoData.code_url = data.data.code_url;
        // 进行第二步
        this.payStep = 2;
        payStatusInterval.push(setTimeout(this.checkPayStatus, 5000));
        console.log(data.data);
      });
    },
    getOrderData(order_id) {
      getOrderDetail({ order_id: order_id }).then(data => {
        console.log(data);
        Object.assign(this.steptwoData, data.data);
        this.steptwoData = data.data;
      });
    },
    cityChoose(e) {
      console.log(e);
      console.log(this.orderData.city);
    },
    checkPayStatus(ifClick = false) {
      getPayStatus({ order_id: this.orderId })
        .then(data => {
          while (payStatusInterval.length != 0) {
            clearTimeout(payStatusInterval.pop());
          }
          console.log("支付成功");
          this.$message({
            message: "支付成功",
            type: "success"
          });

          this.payStep = 3;
        })
        .catch(err => {
          if (ifClick) {
            this.$message({
              message: "尚未支付成功",
              type: "warning"
            });
          }
          while (payStatusInterval.length != 0) {
            clearTimeout(payStatusInterval.pop());
          }

          payStatusInterval.push(setTimeout(this.checkPayStatus, 5000));
        });
    },
    showAgreement() {
      this.agreementShow = true;
      this.agreementCount = 3;
      this.countTimeout();
    },
    countTimeout() {
      if (this.agreementCount > 0) {
        setTimeout(() => {
          this.agreementCount--;
          if (this.agreementCount > 0) {
            this.countTimeout();
          }
        }, 1000);
      } 
    }
  },
  created() {},
  mounted() {
    let jumpQuery = this.$route.query;
    console.log(jumpQuery);
    // 订单信息
    let serviceList = [];
    // .appData
    serviceList.push(jumpQuery);
    this.serviceList = serviceList;
    this.orderData.order_money = jumpQuery
      ? jumpQuery.order_money
      : 0;

    //邮寄地址数据
    this.cityOptions = addressJson;
    if (jumpQuery.orderId) {
      this.orderId = jumpQuery.orderId;
      this.getOrderData(jumpQuery.orderId);
      this.takePayCode(jumpQuery.orderId);
    } else {
      this.payStep = 1;
    }
  },
  updated() {},
  activated() {},
  deactivated() {},
  beforeDestroy() {},
  destroyed() {}
};
</script>

 <style lang="stylus" scoped>
 .orderConfirm {
   width: 67.5%;
   min-width: 1200px;
   margin: 30px auto;

   .messageConfirmBox {
     padding: 30px;
     background-color: #fff;

     .stepsContainer {
       width: 500px;
       margin: 40px auto;
     }

     .serviceTable {
     }

     .addressBox {
       margin-top: 18px;
       padding-bottom: 20px;
       background-color: #f6f8fb;

       .appDetailBar {
         height: 60px;
         margin: auto;
         align-items: center;
         display: flex;

         .detailLeft {
           display: inline-block;
           width: 60px;
           text-align: right;
           vertical-align: top;
           flex: 1;
         }

         .detailRight {
           margin-left: 30px;
           display: inline-block;
           text-align: left;
           flex: 2;

           .el-input--medium {
             width: 240px;
           }

           .el-cascader--medium {
             width: 240px;
           }
         }

         .detailRightLong {
           .el-input--medium {
             width: 500px;
           }
         }
       }
     }

     .stepTwo {
       width: 500px;
       margin: auto;
       padding: 30px;
       border: 1px solid #eaf0f8;
       border-top: 2px solid #0084ff;
       color: #8690ac;
       font-size: 14px;
       line-height: 21px;

       .scanBox {
         .qrcodeBox {
           display: flex;
           justify-content: center;
         }

         .payHelpBar {
           display: flex;
           align-items: center;
           justify-content: center;

           .payHelpFont {
             color: #3a3d57;
             font-size: 14px;
           }

           .midBorder {
             height: 21px;
             border-right: 1px solid #3a3d57;
             margin: 0 15px;
           }
         }
       }
     }

     .stepThree {
       width: 66.67%;
       min-width: 800px;
       margin: auto;
       padding: 50px 0;

       .el-icon-circle-check {
         font-size: 80px;
         color: #4cd663;
         display: block;
         margin: auto;
         text-align: center;
       }

       .bigFont {
         text-align: center;
         font-size: 24px;
         margin: 30px 0;
       }

       .successTips {
         padding: 30px 60px;
         background-color: #f6f8fb;

         .tipsTitle {
           font-size: 16px;
         }

         .tipsBar {
           color: #8690ac;
         }
       }

       .btnBar {
         display: flex;
         justify-content: center;
         margin: 30px 0;
       }
     }

     .toBlack {
       width: 100%;
       height: 100%;
       position: fixed;
       top: 0;
       left: 0;
       z-index: 11;
       background-color: rgba(0, 0, 0, 0.4);
     }

     .agreementContainer {
       width: 800px;
       height: 640px;
       background-color: #fff;
       color: #3a3d57;
       position: fixed;
       left: 50%;
       top: 50%;
       transform: translate(-50%, -50%);
       z-index: 12;

       .agreementTitle {
         height: 60px;
         line-height: 60px;
         font-size: 20px;
         text-indent: 20px;
         border-bottom: 1px solid #f6f8fb;
       }

       .agreementContentContainer::-webkit-scrollbar {
         display: none;
       }

       .agreementContentContainer {
         height: 480px;
         padding: 20px;
         overflow: scroll;

         .agreementShortContent {
           line-height: 36px;
           font-size: 18px;

           .shortTitle {
             font-size: 22px;
             font-weight: bold;
           }

           .agreementDetail {
           }
         }
       }

       .btnBar {
         height: 60px;
         display: flex;
         align-items: center;
         justify-content: flex-end;
         padding-right: 20px;

         .el-button {
           width: 100px;
         }
       }
     }
   }

   .payBox {
     padding: 30px;
     margin: 30px 0;
     background-color: #fff;
     font-size: 16px;

     .payTypeBoxWrap {
       display: inline-block;

       .payTypeBox {
         border: 1px solid #f6f8fb;
         position: relative;
         width: 160px;
         height: 50px;
         line-height: 50px;
         text-align: center;
         margin-right: 20px;
         font-size: 14px;

         .el-icon-check {
           position: absolute;
           top: 1px;
           right: 1px;
           z-index: 2;
           font-size: 14px;
           color: #fff;
         }
       }

       .payTypeChosen {
         border-color: #409eff !important;
         position: relative;
       }

       .payTypeChosen::after {
         content: '';
         position: absolute;
         width: 0px;
         height: 0;
         border: 20px solid rgba(255, 255, 255, 0);
         border-left-color: #409eff !important;
         top: -20px;
         right: -20px;
         transform: rotate(-45deg);
       }
     }

     .agreementBar {
       text-align: right;
       display: flex;
       align-items: center;
       justify-content: flex-end;
       margin: 20px 0;

       .agreementCheck {
         margin: 0 10px 0 0 !important;
       }

       .el-button {
         padding: 0 !important;
       }
     }

     .actBar {
       display: flex;
       align-items: center;
       justify-content: flex-end;
       font-size: 14px;

       .redFont {
         font-size: 20px;
         color: #f86b6e;
       }

       .el-button--primary {
         margin-left: 20px;
       }
     }
   }
 }
</style>
