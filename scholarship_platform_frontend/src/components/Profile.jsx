import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Textarea } from '@/components/ui/textarea'
import { Progress } from '@/components/ui/progress'
import Sidebar from './Sidebar'


const Profile = ({ user, onLogout }) => {
  const [formData, setFormData] = useState({
    full_name: '',
    email: '',
    state_of_origin: '',
    gender: '',
    religion: '',
    level_of_study: '',
    institution: '',
    course_of_study: '',
    academic_performance: '',
    skills_interests: ''
  })
  const [completion, setCompletion] = useState({ completion_percentage: 0 })
  const [message, setMessage] = useState('')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    fetchProfile()
    fetchCompletion()
  }, [])

  const fetchProfile = async () => {
    try {
      const response = await fetch('/api/profile/',{
        credentials: 'include'
      })
      if (response.ok) {
        const data = await response.json()
        setFormData(data);
      } else if (response.status === 401) {
        setMessage('Please log in to view your profile.');
        // if (typeof onLogout === 'function') onLogout()
      }
    } catch (error) {
      console.error('Failed to fetch profile:', error)
      setMessage('Error loading profile. Try again later.');
    }
  }

  const fetchCompletion = async () => {
    try {
      const response = await fetch('/api/profile/completion', {
        credentials: 'include'
      })
      if (response.ok) {  
        const data = await response.json()
        setCompletion(data)
      } else if (response.status === 401) {
        setMessage('Please log in to view your profile.');
        // if (typeof onLogout === 'function') onLogout()
      }
    } catch (error) {
      console.error('Failed to fetch completion:', error)
      setMessage('Error loading profile completion. Try again later.')
    }
  }

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
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
    setMessage('')

    try {
      const response = await fetch('/api/profile/', {
        method: 'PUT',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      })

      const data = await response.json()

      if (response.ok) {
        setMessage('Profile updated successfully!')
        fetchCompletion() // Refresh completion percentage
      } else if (response.status === 401) {
        setMessage('Please log in to update your profile.')
        // if (typeof onLogout === 'function') onLogout()
      } else {
        setMessage(data.error || 'Update failed')
      }
    } catch (error) {
      setMessage('Network error. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 flex">
      <Sidebar user={user} onLogout={onLogout} />
      
      <div className="flex-1 p-6">
        <div className="max-w-4xl mx-auto">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Profile Overview</h1>
            <p className="text-gray-600">
              Manage your personal information and academic details
            </p>
          </div>

          {/* Profile Completion */}
          <Card className="mb-8">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <div className="w-3 h-3 bg-teal-600 rounded-full"></div>
                Profile Completion
              </CardTitle>
              <CardDescription>
                Your profile is {completion.completion_percentage}% complete. 
                Add more details for better scholarship matches.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Progress value={completion.completion_percentage} className="w-full" />
            </CardContent>
          </Card>

          {/* Profile Form */}
          <Card>
            <CardHeader>
              <CardTitle>Personal Information</CardTitle>
              <Button className="ml-auto bg-teal-600 hover:bg-teal-700">
                Edit Profile
              </Button>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-6">
                {message && (
                  <Alert className={message.includes('success') ? 'border-green-200 bg-green-50' : ''}>
                    <AlertDescription>{message}</AlertDescription>
                  </Alert>
                )}

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <Label htmlFor="full_name">Full Name</Label>
                    <Input
                      id="full_name"
                      name="full_name"
                      value={formData.full_name}
                      onChange={handleChange}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="email">Email</Label>
                    <Input
                      id="email"
                      name="email"
                      type="email"
                      value={formData.email}
                      disabled
                      className="bg-gray-50"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="state_of_origin">State of Origin</Label>
                    <Input
                      id="state_of_origin"
                      name="state_of_origin"
                      value={formData.state_of_origin}
                      onChange={handleChange}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label>Gender</Label>
                    <Select 
                      value={formData.gender} 
                      onValueChange={(value) => handleSelectChange('gender', value)}
                    >
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
                      value={formData.religion}
                      onChange={handleChange}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label>Level of Study</Label>
                    <Select 
                      value={formData.level_of_study} 
                      onValueChange={(value) => handleSelectChange('level_of_study', value)}
                    >
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
                      value={formData.institution}
                      onChange={handleChange}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="course_of_study">Course of Study</Label>
                    <Input
                      id="course_of_study"
                      name="course_of_study"
                      value={formData.course_of_study}
                      onChange={handleChange}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="academic_performance">Academic Performance</Label>
                    <Input
                      id="academic_performance"
                      name="academic_performance"
                      placeholder="E.g. CGPA: 4.25, Level: 300"
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
                    rows={4}
                  />
                </div>

                <div className="space-y-4">
                  <h3 className="text-lg font-semibold">Supporting Documents</h3>
                  <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
                    <p className="text-gray-500 mb-2">Upload Document</p>
                    <Button variant="outline" size="sm">
                      Select file
                    </Button>
                    <Button className="ml-2 bg-teal-100 text-teal-700 hover:bg-teal-200" size="sm">
                      Upload
                    </Button>
                  </div>
                </div>

                <Button 
                  type="submit" 
                  className="w-full bg-teal-600 hover:bg-teal-700"
                  disabled={loading}
                >
                  {loading ? 'Updating...' : 'Update Profile'}
                </Button>
              </form>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}

export default Profile

