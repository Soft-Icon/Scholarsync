import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Textarea } from '@/components/ui/textarea'
import Sidebar from './Sidebar'

const AdminPanel = ({ user, onLogout }) => {
  const [formData, setFormData] = useState({
    title: '',
    provider_organization: '',
    deadline: '',
    country: '',
    level_of_study: '',
    field_of_study: '',
    eligibility: '',
    amount_benefits: '',
    application_link: '',
    contact_email: '',
    supporting_files: ''
  })
  const [message, setMessage] = useState('')
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
    setMessage('')

    try {
      const response = await fetch('/api/scholarships/', {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      })

      const data = await response.json()

      if (response.ok) {
        setMessage('Scholarship added successfully!')
        setFormData({
          title: '',
          provider_organization: '',
          deadline: '',
          country: '',
          level_of_study: '',
          field_of_study: '',
          eligibility: '',
          amount_benefits: '',
          application_link: '',
          contact_email: '',
          supporting_files: ''
        })
      } else {
        setMessage(data.error || 'Failed to add scholarship')
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
            <nav className="text-sm text-gray-500 mb-2">
              Dashboard › Scholarships › Add
            </nav>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Add Scholarship</h1>
            <p className="text-gray-600">
              Enter scholarship details below. All fields except contact email are required.
            </p>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Scholarship Details</CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-6">
                {message && (
                  <Alert className={message.includes('success') ? 'border-green-200 bg-green-50' : ''}>
                    <AlertDescription>{message}</AlertDescription>
                  </Alert>
                )}

                <div className="space-y-2">
                  <Label htmlFor="title">Scholarship Name</Label>
                  <Input
                    id="title"
                    name="title"
                    placeholder="e.g. MTN Foundation Scholarship"
                    value={formData.title}
                    onChange={handleChange}
                    required
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="provider_organization">Provider/Organization Name</Label>
                  <Input
                    id="provider_organization"
                    name="provider_organization"
                    placeholder="e.g. MTN Foundation"
                    value={formData.provider_organization}
                    onChange={handleChange}
                  />
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <Label htmlFor="deadline">Application Deadline</Label>
                    <Input
                      id="deadline"
                      name="deadline"
                      type="date"
                      value={formData.deadline}
                      onChange={handleChange}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="country">Country of Scholarship</Label>
                    <Input
                      id="country"
                      name="country"
                      placeholder="e.g. Nigeria"
                      value={formData.country}
                      onChange={handleChange}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label>Level of Study</Label>
                    <Select onValueChange={(value) => handleSelectChange('level_of_study', value)}>
                      <SelectTrigger>
                        <SelectValue placeholder="Undergraduate, Masters, PhD" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="undergraduate">Undergraduate</SelectItem>
                        <SelectItem value="masters">Masters</SelectItem>
                        <SelectItem value="phd">PhD</SelectItem>
                        <SelectItem value="all">All Levels</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="field_of_study">Field of Study</Label>
                    <Input
                      id="field_of_study"
                      name="field_of_study"
                      placeholder="e.g. Engineering, Medicine"
                      value={formData.field_of_study}
                      onChange={handleChange}
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="eligibility">Eligibility Criteria</Label>
                  <Textarea
                    id="eligibility"
                    name="eligibility"
                    placeholder="Describe who can apply"
                    value={formData.eligibility}
                    onChange={handleChange}
                    rows={4}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="amount_benefits">Scholarship Amount/Benefits</Label>
                  <Input
                    id="amount_benefits"
                    name="amount_benefits"
                    placeholder="e.g. ₦200,000 per year, tuition, stipend"
                    value={formData.amount_benefits}
                    onChange={handleChange}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="application_link">Application Link</Label>
                  <Input
                    id="application_link"
                    name="application_link"
                    placeholder="Paste application URL"
                    value={formData.application_link}
                    onChange={handleChange}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="contact_email">Contact Email (optional)</Label>
                  <Input
                    id="contact_email"
                    name="contact_email"
                    type="email"
                    placeholder="e.g. info@provider.org"
                    value={formData.contact_email}
                    onChange={handleChange}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="supporting_files">Upload Supporting Files</Label>
                  <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
                    <p className="text-gray-500 mb-2">Attach PDF flyer or document</p>
                    <Button variant="outline" size="sm" type="button">
                      Select file
                    </Button>
                  </div>
                </div>

                <Button 
                  type="submit" 
                  className="w-full bg-teal-600 hover:bg-teal-700"
                  disabled={loading}
                >
                  {loading ? 'Adding Scholarship...' : 'Submit Scholarship'}
                </Button>
              </form>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}

export default AdminPanel

