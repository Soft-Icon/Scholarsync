import { useState } from 'react'
import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Textarea } from '@/components/ui/textarea'

const Signup = ({ onSignup }) => {
  const [formData, setFormData] = useState({
    full_name: '',
    email: '',
    password: '',
    state_of_origin: '',
    gender: '',
    religion: '',
    level_of_study: '',
    institution: '',
    course_of_study: '',
    academic_performance: '',
    skills_interests: ''
  })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    })
  }

  const handleSelectChange = (name, value) => {
    setFormData({
      ...formData,
      [name]: value
    })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      const response = await fetch('/api/auth/signup', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      })

      const data = await response.json()

      if (response.ok) {
        // Auto-login after successful signup
        const loginResponse = await fetch('/api/auth/login', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            email: formData.email,
            password: formData.password
          }),
        })

        if (loginResponse.ok) {
          const loginData = await loginResponse.json()
          onSignup(loginData.user)
        }
      } else {
        setError(data.error || 'Signup failed')
      }
    } catch (error) {
      setError('Network error. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-teal-50 to-blue-50 p-4">
      <Card className="w-full max-w-2xl">
        <CardHeader className="text-center">
          <CardTitle className="text-2xl font-bold text-gray-900">Create Account</CardTitle>
          <CardDescription className="text-gray-600">
            Join ScholarSync to discover scholarships tailored for you.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            {error && (
              <Alert variant="destructive">
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="full_name">Full Name</Label>
                <Input
                  id="full_name"
                  name="full_name"
                  placeholder="Enter your full name"
                  value={formData.full_name}
                  onChange={handleChange}
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  name="email"
                  type="email"
                  placeholder="Enter your email address"
                  value={formData.email}
                  onChange={handleChange}
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="password">Password</Label>
                <Input
                  id="password"
                  name="password"
                  type="password"
                  placeholder="Create a password"
                  value={formData.password}
                  onChange={handleChange}
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="state_of_origin">State of Origin</Label>
                <Input
                  id="state_of_origin"
                  name="state_of_origin"
                  placeholder="Enter your state of origin"
                  value={formData.state_of_origin}
                  onChange={handleChange}
                />
              </div>

              <div className="space-y-2">
                <Label>Gender</Label>
                <Select onValueChange={(value) => handleSelectChange('gender', value)}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select your gender" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="male">Male</SelectItem>
                    <SelectItem value="female">Female</SelectItem>
                    <SelectItem value="other">Other</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="religion">Religion</Label>
                <Input
                  id="religion"
                  name="religion"
                  placeholder="Enter your religion"
                  value={formData.religion}
                  onChange={handleChange}
                />
              </div>

              <div className="space-y-2">
                <Label>Level of Study</Label>
                <Select onValueChange={(value) => handleSelectChange('level_of_study', value)}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select your level" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="undergraduate">Undergraduate</SelectItem>
                    <SelectItem value="masters">Masters</SelectItem>
                    <SelectItem value="phd">PhD</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="institution">Institution</Label>
                <Input
                  id="institution"
                  name="institution"
                  placeholder="Enter your institution"
                  value={formData.institution}
                  onChange={handleChange}
                />
              </div>

              <div className="space-y-2 md:col-span-2">
                <Label htmlFor="course_of_study">Course of Study</Label>
                <Input
                  id="course_of_study"
                  name="course_of_study"
                  placeholder="Enter your course"
                  value={formData.course_of_study}
                  onChange={handleChange}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="academic_performance">Academic Performance</Label>
                <Input
                  id="academic_performance"
                  name="academic_performance"
                  placeholder="E.g. CGPA, Grade"
                  value={formData.academic_performance}
                  onChange={handleChange}
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="skills_interests">Skills & Interests</Label>
              <Textarea
                id="skills_interests"
                name="skills_interests"
                placeholder="Add skills or interests"
                value={formData.skills_interests}
                onChange={handleChange}
                rows={3}
              />
            </div>

            <Button 
              type="submit" 
              className="w-full bg-teal-600 hover:bg-teal-700"
              disabled={loading}
            >
              {loading ? 'Creating Account...' : 'Sign up'}
            </Button>

            <div className="text-center">
              <Link 
                to="/login" 
                className="text-teal-600 hover:text-teal-700 text-sm"
              >
                Already have an account? Log in
              </Link>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}

export default Signup

