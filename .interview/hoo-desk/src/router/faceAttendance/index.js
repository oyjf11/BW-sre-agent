import _layout from "@/views/layout/layout.vue";
const faceAttendanceCenter = () => import(/* webpackChunkName: "group-student" */ '@/components/faceAttendance/faceAttendanceCenter');
const faceAttendanceEquipment = () => import(/* webpackChunkName: "group-student" */ '@/components/faceAttendance/faceAttendanceEquipment');
const faceAttendanceControl = () => import(/* webpackChunkName: "group-student" */ '@/components/faceAttendance/faceAttendanceControl');

let router = {
    name: "appStore",
    text: "人脸考勤",
    path: "/faceAttendance",
    icon: "hoo hoo-createtask icon-lg",
    newicon: "hoo hoo-createtask_fill icon-lg",
    component: _layout,
    meta: { power: ["iface_attendance"] },
    children: [
        {
            name: "faceAttendanCenter",
            // hide: true,
            text: "考勤中心",
            path: "/faceAttendance/center",
            meta: { power: ["iface_attendance"], title: '考勤中心', desc: '考勤中心' },
            route: {
                path: "/faceAttendance/center"
                // query: { newWindow: true }
            },
            component: faceAttendanceCenter
        }, {
            name: "faceAttendanceEquipment",
            // hide: true,
            text: "设备管理",
            path: "/faceAttendance/equipment",
            meta: { power: ["iface_attendance"], title: '设备管理', desc: '设备管理' },
            route: {
                path: "/faceAttendance/equipment"
            },

            component: faceAttendanceEquipment
        }, {
            name: "faceAttendanceControl",
            // hide: true,
            text: "人脸管理",
            path: "/faceAttendance/control",
            meta: { power: ["iface_attendance"], title: '人脸管理', desc: '人脸管理' },
            route: {
                path: "/faceAttendance/control"
            },

            component: faceAttendanceControl
        }
    ]
}
export default router;