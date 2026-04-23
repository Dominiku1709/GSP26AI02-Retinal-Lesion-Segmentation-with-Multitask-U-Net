"use client"
// This component is a modal for creating a new patient. It includes form fields for name, date of birth, and

import { useState, useMemo } from "react"
import { useAppState } from "@/lib/store"
import { X } from "lucide-react"
import { cn } from "@/lib/utils"


function computeAge(dateStr: string) {
  if (!dateStr) return 0
  const today = new Date()
  const birth = new Date(dateStr)
  let age = today.getFullYear() - birth.getFullYear()
  const m = today.getMonth() - birth.getMonth()
  if (m < 0 || (m === 0 && today.getDate() < birth.getDate())) age--
  return age
}

export function NewPatientModal() {
  const { newPatientModalOpen, setNewPatientModalOpen, addNewPatient } = useAppState()
  
  const [name, setName] = useState("")
  const [dobDay, setDobDay] = useState("")
  const [dobMonth, setDobMonth] = useState("") 
  const [dobYear, setDobYear] = useState("")
  const [gender, setGender] = useState("Male")

  const currentYear = new Date().getFullYear()
  const years = Array.from({ length: 121 }, (_, i) => (currentYear - i).toString())
  const months = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
  ]

  const daysInMonth = useMemo(() => {
    if (!dobMonth || !dobYear) return 31
    return new Date(parseInt(dobYear), parseInt(dobMonth) + 1, 0).getDate()
  }, [dobMonth, dobYear])

  const days = Array.from({ length: daysInMonth }, (_, i) => (i + 1).toString())

  // 1. Function Validator: Kiểm tra ngày sinh hợp lệ
  const isValidDOB = (day: string, month: string, year: string) => {
    if (!day || !month || !year) return false
    
    const selectedDate = new Date(parseInt(year), parseInt(month), parseInt(day))
    const today = new Date()
    
    // Đặt giờ về 0 để chỉ so sánh ngày/tháng/năm
    today.setHours(0, 0, 0, 0)
    
    // Trả về true nếu ngày chọn nhỏ hơn hoặc bằng ngày hiện tại
    return selectedDate <= today
  }

  const getISODate = () => {
    if (!dobDay || !dobMonth || !dobYear) return ""
    const month = (parseInt(dobMonth) + 1).toString().padStart(2, '0')
    const day = dobDay.padStart(2, '0')
    return `${dobYear}-${month}-${day}`
  }

  const reset = () => {
    setName("")
    setDobDay("")
    setDobMonth("")
    setDobYear("")
    setGender("Male")
  }

  const handleClose = () => {
    setNewPatientModalOpen(false)
    reset()
  }

  // 2. Cập nhật logic Submit
  const handleSubmit = () => {
    if (!name.trim()) return

    // Kiểm tra validator trước khi lưu
    if (!isValidDOB(dobDay, dobMonth, dobYear)) {
      alert("Ngày sinh không hợp lệ ")
      return // Dừng lại ở đây, form vẫn mở
    }

    addNewPatient({
      name: name.trim(),
      dob: getISODate(),
      gender,
    })
    handleClose()
  }

  if (!newPatientModalOpen) return null

  const isoDate = getISODate()
  // Kiểm tra nhanh để disable nút Create nếu chưa nhập đủ thông tin
  const isFormIncomplete = !name.trim() || !dobDay || !dobMonth || !dobYear

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-background/80 backdrop-blur-sm">
      <div className="w-full max-w-sm rounded-xl border border-border bg-card p-6 shadow-lg">
        <div className="flex items-center justify-between mb-5">
          <h2 className="text-base font-semibold text-foreground">New Patient</h2>
          <button onClick={handleClose} className="rounded-md p-1.5 text-muted-foreground hover:bg-muted">
            <X className="h-4 w-4" />
          </button>
        </div>

        <div className="flex flex-col gap-4">
          {/* Name */}
          <div className="flex flex-col gap-1.5">
            <label className="text-xs font-medium text-foreground">
              Full Name <span className="text-destructive">*</span>
            </label>
            <input
              type="text"
              placeholder="e.g. Jane Smith"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full rounded-lg border border-input bg-background px-3 py-2 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
            />
          </div>

          {/* DOB Dropdowns */}
          <div className="flex flex-col gap-1.5">
            <label className="text-xs font-medium text-foreground">Date of Birth</label>
            <div className="flex gap-2">
              <select
                value={dobMonth}
                onChange={(e) => {
                  setDobMonth(e.target.value)
                  setDobDay("")
                }}
                className="flex-[2] rounded-lg border border-input bg-background px-2 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
              >
                <option value="">Month</option>
                {months.map((m, i) => <option key={m} value={i}>{m}</option>)}
              </select>

              <select
                value={dobDay}
                onChange={(e) => setDobDay(e.target.value)}
                className="flex-1 rounded-lg border border-input bg-background px-2 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
              >
                <option value="">Day</option>
                {days.map((d) => <option key={d} value={d}>{d}</option>)}
              </select>

              <select
                value={dobYear}
                onChange={(e) => {
                  setDobYear(e.target.value)
                  setDobDay("")
                }}
                className="flex-1 rounded-lg border border-input bg-background px-2 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
              >
                <option value="">Year</option>
                {years.map((y) => <option key={y} value={y}>{y}</option>)}
              </select>
            </div>
            {isoDate && (
              <p className="text-[10px] text-muted-foreground mt-1 text-right">
                Age: <span className="font-bold text-foreground">{computeAge(isoDate)}y</span>
              </p>
            )}
          </div>

          {/* Gender */}
          <div className="flex flex-col gap-1.5">
            <label className="text-xs font-medium text-foreground">Gender</label>
            <div className="flex rounded-lg bg-muted p-0.5">
              {["Male", "Female"].map((g) => (
                <button
                  key={g}
                  type="button"
                  onClick={() => setGender(g)}
                  className={cn(
                    "flex-1 rounded-md py-1.5 text-xs font-medium transition-all",
                    gender === g
                      ? "bg-card text-foreground shadow-sm"
                      : "text-muted-foreground hover:text-foreground"
                  )}
                >
                  {g}
                </button>
              ))}
            </div>
          </div>
        </div>

        <div className="flex gap-2 mt-6">
          <button
            onClick={handleClose}
            className="flex-1 rounded-lg border border-border bg-card py-2 text-sm font-medium text-foreground hover:bg-muted transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={handleSubmit}
            disabled={isFormIncomplete}
            className="flex-1 rounded-lg bg-primary py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-40 transition-colors"
          >
            Create Patient
          </button>
        </div>
      </div>
    </div>
  )
}